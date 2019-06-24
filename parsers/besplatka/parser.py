import requests
from lxml import html
from pprint import pprint
import re


class Besplatka:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    }

    @staticmethod
    def phone_format(phone):
        phone = '38' + phone if phone[0:2] != '38' and phone[0:3] != '+38' else phone
        phone = '+' + phone if phone[0:1] != '+' else phone
        return phone

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
            print(req.status_code)
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

            pprint(car_info)
            return car_info

        return None
