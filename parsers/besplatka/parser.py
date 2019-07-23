import requests
from django.db.models import Q
from django.utils import timezone
from lxml import html
from pprint import pprint
import re

from main.models import SellerPhone, Car
from parsers.auto_ria.parser import WordsFormater
from parsers.choises import GEARBOX, LOCATION_bp, BODY, FUEL
from parsers.utils import get_model_id


class Besplatka(WordsFormater):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    }
    body = []
    post_body = None
    current_link = None
    base_way = 'https://besplatka.ua/transport/legkovye-avtomobili/page/{}'
    root_way = 'https://besplatka.ua{}'


    def set_saller(self, phones):
        query = Q()
        for phone in phones:
            query = query | Q(phone__contains=phone)
        seller = SellerPhone.objects.filter(query).first()
        return seller

    def set_car(self, car_dict: dict):
        car = dict(models_id=get_model_id(car_dict['mark'], car_dict['model']),
                   gearbox_id=GEARBOX_ab.get(car_dict['gearbox']),
                   location_id=LOCATION.get(
                       car_dict['location']),
                   fuel_id=FUEL_ab.get(
                       car_dict['fuel']),
                   engine=self.engine_parse(
                       car_dict['autoData']['fuelName']),
                   color=None,
                   year=car_dict['autoData']['year'],
                   mileage=car_dict['autoData'][
                       'raceInt'],
                   seller=self.set_saller(
                       car_dict['userPhoneData']['phone']),
                   body_id=(BODY_ab.get(car_dict['body'])),
                   image=
                   car_dict['photoData']['seoLinkF'],
                   dtp=self.check_dtp(car_dict['infoBarText']),
                   sold=car_dict['autoData']['isSold'],
                   cleared=not bool(car_dict['autoData']['custom']),
                   ria_link='https://auto.ria.com' + car_dict['linkToView'],
                   createdAt=self.format_date(car_dict['addDate']),
                   updatedAt=timezone.now(),
                   last_site_updatedAt=self.format_date(
                       car_dict['updateDate'])
                   )
        return None

    @staticmethod
    def phone_format(phone):
        phone = '38' + phone if phone[0:2] != '38' and phone[0:3] != '+38' else phone
        phone = '+' + phone if phone[0:1] != '+' else phone
        return phone[3:]

    def get_count_pages(self):
        url = 'https://besplatka.ua/transport/legkovye-avtomobili'
        req = requests.get(url, headers=self.headers)
        body = html.document_fromstring(req.text)
        pages = body.xpath('//div[@id="pagination"]/div/ul/li[12]/a/text()')[0]
        return int(pages[0])

    def get_urls_by_page(self, page):
        url = 'https://besplatka.ua/transport/legkovye-avtomobili/page/{0}'
        req = requests.get(url.format(page), headers=self.headers)
        body = html.document_fromstring(req.text)
        autos_urls = body.xpath('//div[@id="servermessages"]/div/div/div/div[3]/a/@href')
        result_urls = []
        for url in autos_urls:
            result_urls.append('https://besplatka.ua' + url)
        return result_urls

    def get_info_by_url(self, url):
        req = requests.get(url, headers=self.headers)
        body = html.document_fromstring(req.text)

        car_info = {'sold': 0, 'dtp': 0, 'car_key': url.split('-')[-1], 'url': url}

        if req.status_code != requests.codes.ok:
            # print(req.status_code)
            car_info['sold'] = 1

        # Получаем цену по микроразметке
        currency = body.xpath('//meta[contains(@itemprop, "priceCurrency")]/@content')[0]
        price_value = body.xpath('//meta[@itemprop="price"]/@content')[0]

        if not car_info['sold'] and int(price_value) != -1:
            car_info['price'] = int(price_value)
            car_info['currency'] = currency
            csrf = body.xpath('//meta[@name="csrf-token"]/@content')[0]
            car_id = body.xpath('//a[@class="show-phone"]/@data-id')
            if not car_id:
                car_info['sold'] = 1
                return car_info
            car_id = car_id[0]
            headers = {'referer': url, 'x-csrf-token': csrf, 'x-requested-with': 'XMLHttpRequest'}
            phones = requests.post('https://besplatka.ua/message/show-phone', data={'id': car_id},
                                   headers=headers).text.split(',')
            car_info['phones'] = [
                self.phone_format(x.replace(" ", "").replace("-", "").replace("(", "").replace(")", ""))
                for x in phones if x
            ]
            # Основные параметры по мнению бесплатки
            properties = body.xpath('//div[@class="mes-properties"]/div/div[@class="property"]')
            for prop in properties:
                prop_name = prop[0].text_content()
                if prop_name == 'Модель':
                    maker = prop[1][0].attrib['href'].split('/')
                    car_info['mark'] = maker[-2]
                    car_info['model'] = maker[-1]
                elif prop_name == 'Год выпуска':
                    car_info['year'] = prop[1].text_content().strip()
                elif prop_name == 'Топливо':
                    car_info['fuel'] = prop[1][0].attrib['href'].split('/')[-1]
                elif prop_name == 'Тип кузова':
                    car_info['body'] = prop[1][0].attrib['href'].split('/')[-1]
                elif prop_name == 'Тип КПП':
                    car_info['gearbox'] = prop[1][0].attrib['href'].split('/')[-1]
                elif prop_name == 'Состояние' and prop[1][0].attrib['href'].split('/')[-1] == 'posle-dtp':
                    car_info['dtp'] = 1

            # Дополнительные параметры по мнению бесплатки
            other_properties = body.xpath('//div[@class="property-row-other"]/div[@class="row-property"]')
            for prop in other_properties:
                prop_name = prop[0].text_content()
                if prop_name == 'Цвет':
                    car_info['color'] = prop[1].text_content().strip()
                elif prop_name == 'Пробег':
                    car_info['mileage'] = int(re.sub('[^0-9]', '', prop[1].text_content().strip()))
                    if car_info['mileage'] > 0 and car_info['mileage'] < 500:
                        car_info['mileage'] *= 1000
                elif prop_name == 'Объем двигателя':
                    car_info['engine'] = re.sub('[^0-9\,]', '', prop[1].text_content().strip())
                    car_info['engine'] = re.sub('\,', '.', car_info['engine'])
                elif prop_name == 'Растаможена' and prop[1].text_content().strip() == 'Не растаможена':
                    car_info['customs'] = 1

            try:
                car_info['user_name'] = body.xpath('//div[@class="add-user-name"]/a/text()')[0].strip()
            except:
                pass

            car_info['city_id'] = body.xpath('//div[@id="message"]/div[2]/div/ul/li[1]/text()')[0].strip()
            car_info['createdAt'] = body.xpath('//div[@id="message"]/div[2]/div/ul/li[2]/text()')[0].strip()
            car_info['description'] = body.xpath('//div[contains(@itemprop, "description")]/text()')[0].strip()
            car_info['photos'] = body.xpath(
                '//ul[contains(@class, "ms-slider")]/li/a/*[self::div or self::span]/img/@data-src'
            )

            pprint(car_info['gearbox'])
            # if car_info['body'] in self.body:
            # self.body.append(car_info['body'])
            # return car_info
            return None

    def get_mark_model_name(self) -> tuple:
        splitted_link = self.post_body.xpath('//*[@id="message"]/div[5]/div[1]/div[1]/div[2]/a/@href')[0].split('/')
        return (splitted_link[-2].strip(), splitted_link[-1].strip(),)

    def parse_engine(self) -> float or None:
        line = self.post_body.xpath('//*[@id="message"]/div[7]/div[2]/div[2]/div[2]/text()')[0]
        if line.match('литра'):
            return float(line[:line.find(' ')].replace(',', '.'))
        return None

    def parse_mileage(self) -> int or None:
        line = self.post_body.xpath('//*[@id="message"]/div[7]/div[2]/div[1]/div[2]/text()')[0]
        if line.match('км'):
            return int(line[:line.find(' ')]) // 1000
        return None

    @staticmethod
    def create_seller(phones: list) -> SellerPhone:
        seller = SellerPhone(phone=' ,'.join(phones))
        seller.save()
        return seller

    def parse_seller(self) -> SellerPhone:
        query = Q()
        csrf = self.post_body.xpath('//meta[@name="csrf-token"]/@content')[0]
        car_id = self.post_body.xpath('//a[@class="show-phone"]/@data-id')
        local_headers = {'referer': self.current_link, 'x-csrf-token': csrf, 'x-requested-with': 'XMLHttpRequest'}
        phones = requests.post('https://besplatka.ua/message/show-phone', data={'id': car_id}, headers=local_headers).text.split(',')
        phones = [phone.replace('+', '').strip() for phone in phones][:-1]
        for phone in phones:
            query = query | Q(phone__contains=phone)
        seller = SellerPhone.objects.filter(query).first()
        if seller is None:
            seller = self.create_seller(phones)
        return seller

    def find_car_data(self) -> dict:
        response = dict()
        r = 3 + 'e3'
        response['location_id'] = LOCATION_bp.get(self.post_body.xpath('//*[@id="open-region-modal"]/@data-region-id')[0])
        response['model_id'] = get_model_id(*self.get_mark_model_name())
        response['gearbox_id'] = GEARBOX.get(self.post_body.xpath('//*[@id="message"]/div[5]/div[2]/div[3]/div[2]/a/text()')[0].lower())
        response['fuel_id'] = FUEL.get(self.post_body.xpath('//*[@id="message"]/div[5]/div[2]/div[1]/div[2]/a/text()')[0].lower())
        response['year'] = int(self.post_body.xpath('//*[@id="message"]/div[5]/div[1]/div[3]/div[2]/text()').strip())
        response['body_id'] = BODY.get(self.post_body.xpath('//*[@id="message"]/div[5]/div[2]/div[2]/div[2]/a/text()')[0].lower())
        response['mileage'] = self.parse_mileage()
        response['engine'] = self.parse_engine()
        response['seller'] = self.parse_seller()
        response['image'] = self.post_body.xpath('//*[@id="message"]/div[1]/div[1]/ul/li[1]/div/img/@src')[0]
        response['dtp'] = self.post_body.xpath('//*[@id="message"]/div[5]/div[1]/div[2]/div[2]/a/text()')[0].match('После ДТП')
        response['sold'] = None  # тута остановился

        return response

    def parse_post(self) -> Car:
        self.post_body = html.document_fromstring(requests.get(self.current_link, headers=self.headers).text)
        car_data = self.find_car_data()
        return Car(body_id=5)

    def run(self, start: int, finish: int) -> None:
        for page in range(start, finish):
            body = html.document_fromstring(requests.get(self.base_way.format(page), headers=self.headers).text)
            for post in range(1, 30):
                self.current_link = self.root_way.format(body.xpath(f'//*[@id="servermessages"]/div[4]/div[{post}]/div/div[3]/a/@href')[0])
                # print(body.xpath(f'//*[@id="servermessages"]/div[4]/div[{post}]/div/div[3]/a/@href')[0])
                car = self.parse_post()
                return
                # //*[@id="servermessages"]/div[4]/div[30]/div/div[3]/a
            # body = html.document_fromstring(req.text)
