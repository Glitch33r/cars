import time
from datetime import datetime

from django.utils import timezone
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from fake_useragent import UserAgent
from django.core.paginator import Paginator
from main.models import SellerPhone, Car, PriceHistory
from parsers.choises import GEARBOX, FUEL, BODY, LOCATION
from parsers.utils import get_model_id, find_same_car


class ParsDataOLX:
    driver = None

    @staticmethod
    def create_seller(phone: str):
        seller = SellerPhone(phone=phone)
        seller.save()
        return seller

    @staticmethod
    def cleaned_numbers(numbers: str) -> str:
        # print(type(numbers), numbers)
        true_numbers = '0123456789'
        response = ''
        for number in str(numbers):
            if number in true_numbers:
                response += number
        return response

    @staticmethod
    def format_month(date):
        month = {
            'января': '01',
            'февраля': '02',
            'марта': '03',
            'апреля': '04',
            'мая': '05',
            'июня': '06',
            'июля': '07',
            'августа': '08',
            'сентября': '09',
            'октября': '10',
            'ноября': '11',
            'декабря': '12',
        }
        numbers = '0123456789:, '
        response = ''
        for dat in date:
            if dat not in numbers:
                response += dat
        return f'{date[:-5 - (len(response))]}{month.get(response)} {date[-4:]}'

    def format_phone(self, phone: str) -> str:
        return f'38{self.cleaned_numbers(phone)[-10:]}'

    def find_seller(self):
        phone = self.parse_phone()
        if phone is None:
            return None
        seller = SellerPhone.objects.filter(phone__contains=phone).first()
        if seller is None:
            seller = self.create_seller(phone)
        # print(seller)
        return seller

    def parse_phone(self):
        phone = self.xpath('//*[@id="contact_methods"]/li[2]/div/span')
        if phone:
            phone.click()
            count = 0
            while True:
                time.sleep(0.2)
                count += 1
                if 'x' not in self.xpath('//*[@id="contact_methods"]/li[2]/div/strong').text:
                    phone = self.format_phone(self.xpath('//*[@id="contact_methods"]/li[2]/div/strong').text)
                    break
                elif count > 30:
                    print('phone not find')
                    return None
            return phone
        return None

    def xpath(self, str_xpath: str):
        try:
            return self.driver.find_element_by_xpath(str_xpath)
        except NoSuchElementException:
            return None

    def parse_from_base_info(self, name: str, link=False):
        link = '/a' if link else ''
        return self.xpath(f'//*[@id="offerdescription"]//th[contains(text(),"{name}")]/../td/strong{link}')

    def parse_year(self):
        resp = self.parse_from_base_info('Год выпуска')
        if resp:
            return int(resp.text.strip())
        return None

    def parse_gearbox(self):
        gearbox = self.parse_from_base_info('Коробка передач', link=True)
        if gearbox is None:
            return None
        gearbox = gearbox.text.lower().replace(' ', '')
        if gearbox == 'автоматическая':
            gearbox = 'автомат'
        elif gearbox == 'механическая':
            gearbox = 'ручная/механика'
        gear = GEARBOX.get(gearbox, None)
        if gearbox is None:
            # print(f'###########{self.parse_from_base_info("Коробка передач", link=True)}#############################')
            return None
        return gear

    def parse_model(self):
        lines = self.parse_from_base_info('Модель', link=True)
        if lines is None:
            return None
        print('model is find')
        lines = lines.get_attribute("href").split('/')
        if lines[-3] == 'drugaya':
            return None
        print('data car models', lines[-4], lines[-3])
        return get_model_id(lines[-4], lines[-3])

    def parse_fuel(self):
        fuel = self.parse_from_base_info('Вид топлива', link=True)
        if fuel is None:
            return None
        fuel = FUEL.get(fuel.text.lower().replace(' ', ''), None)
        if fuel is None:
            print(f'###########{self.parse_from_base_info("Вид топлива", link=True)}#################################')
            return None
        return fuel

    def parse_engine(self):
        engine = self.parse_from_base_info('Объем двигателя')
        if engine is None:
            return None
        valid_fuel = self.cleaned_numbers(engine)
        return round(float(f'{valid_fuel[0]}.{valid_fuel[1:]}'), 1)

    def parse_description(self):
        descriptions = self.xpath('//div[@id="textContent"]')
        if descriptions is None:
            return None
        return descriptions.text

    def parse_mileage(self):
        mileage = self.parse_from_base_info('Пробег')
        if mileage is None:
            return None
        return int(self.cleaned_numbers(mileage.text)) // 1000

    def parse_body(self):
        body = self.parse_from_base_info('Тип кузова', link=True)
        if body is None:
            return None
        body = body.text.lower().replace(' ', '')
        if body == 'легковойфургон(до1,5т)':
            body = 'легковой фургон'
        return BODY.get(body, None)

    def parse_image(self):
        image = self.xpath('//*[@id="photo-gallery-opener"]/img')
        if image is None:
            return None
        return image.get_attribute('src')

    def parse_dtp(self):
        dtp = self.parse_from_base_info('Состояние машины', link=True)
        if dtp is None:
            return False  # информации по дтп не найдено
        dtp = dtp.text.strip()
        if dtp == 'После ДТП':
            return True
        return False

    def parse_location(self):
        location = self.xpath('//*[@id="offerdescription"]/div[2]/div[1]/a/strong')
        if location is None:
            return None
        location = str(location.text.split(', ')[1].lower())
        return LOCATION.get(location[:location.find(' ')], None)

    def parse_cleared(self):
        cleared = self.parse_from_base_info('Растаможена', link=True)
        if cleared is None:
            return True  # информации по Растаможке не найдено
        if cleared.text == 'Нет':
            return False
        return True

    def parse_link(self):
        return self.driver.current_url

    def parse_date_create(self):
        line = self.xpath('//*[@id="offerdescription"]/div[2]/div[1]/em')
        if line is None:
            return None
        line = line.text
        date = self.format_month(line[line.find(' в ') + 3:line.find(', Номер объявления:')].strip())
        return datetime.strptime(date, '%H:%M, %d %m %Y')

    def parse_price(self):
        line = self.xpath('//*[@id="offeractions"]/div[1]/strong')
        if line is None:
            return None
        line = line.text
        # print(self.cleaned_numbers(line))
        if self.cleaned_numbers(line):
            return int(self.cleaned_numbers(line))
        return None


class OLXInner(ParsDataOLX):
    car = None
    driver = None
    car_dict = None
    chrome_options = None
    links_of_post = []
    proxy_counter = {'local': 0, 'base': 1}
    proxy = {
        # 'address3': '45.67.120.4:30032',
        'address3': '45.67.120.6:30032',
        'address4': '45.67.123.107:30032',
        'address1': '45.67.123.13:30032',
        'address2': '45.67.120.171:30032',
        'username': 'jorjclub0420_gmail_c',
        'password': '2c752798d6'}
    base_way = 'https://www.olx.ua/transport/legkovye-avtomobili/?page={}'

    def __init__(self):
        self.set_driver()
        self.last_pars = self.read_start_time()
        print('set complete')
        self.run()

    def set_driver(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument(f'--proxy={self.proxy["address{}".format(self.proxy_counter["base"])]}')
        self.chrome_options.add_argument(f'--proxy-auth={self.proxy["username"]}:{self.proxy["password"]}')
        self.chrome_options.headless = False
        ua = UserAgent()
        self.chrome_options.add_argument(f'user-agent={ua.random}')

        self.driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=self.chrome_options)
        # chrome_options.binary_location = "/usr/bin/chromium-browser"                                       # for serv
        # self.driver = webdriver.Chrome(executable_path='./chromium_driver', chrome_options=chrome_options) # for serv

    def run(self):
        self.driver.get(self.base_way.format(1))
        self.write_start_time()
        if not self.stack_links():
            print('stay in if in run()')
            self.parse_posts()
        else:
            print('going to else in run()')
            self.parse_posts()
            for page in range(2, 201):
                print('##########################################')
                print(f'################ page  {page} ##################')
                print('###########################################')
                self.driver.get(self.base_way.format(page))
                if self.stack_links():
                    print(len(self.links_of_post), self.links_of_post[1])
                    self.parse_posts()
                else:
                    self.parse_posts()
                    break

    def change_proxy(self):
        current_url = self.driver.current_url
        self.driver.close()
        print(f'PROXY IS CHANGED to No "{self.proxy_counter["base"] + 1 if self.proxy_counter["base"] < 4 else 1}"')
        self.proxy_counter['local'] = 0
        self.proxy_counter['base'] = self.proxy_counter["base"] + 1 if self.proxy_counter["base"] < 4 else 1
        self.set_driver()
        self.driver.get(current_url)

    def check_proxy_counter(self):
        if self.proxy_counter['local'] >= 25:
            self.change_proxy()
        self.proxy_counter['local'] += 1

    def parse_posts(self):
        for link in self.links_of_post:
            if self.check_car_is_present(link):
                print('car present')
                pass
            else:
                self.driver.get(link)
                # print(link)
                self.check_proxy_counter()
                self.parse_data()
                if self.data_valid() is False:
                    pass
                else:
                    self.find_same_car()
                    self.car.save()
                    self.set_price()

    def data_valid(self):
        list_required_keys = ['model_id', 'gearbox_id', 'location_id', 'fuel_id',
                              'year', 'mileage', 'engine', 'seller', 'body_id']
        for key in list_required_keys:
            if self.car_dict.get(key, None) is None:
                print(f'#################### invalid key ####{key}##########')
                return False
        if self.parse_price() is None:
            return False
        return True

    def parse_data(self):
        self.car_dict = {
            'model_id': self.parse_model(),
            'seller': self.find_seller(),
            'year': self.parse_year(),
            'gearbox_id': self.parse_gearbox(),
            'location_id': self.parse_location(),
            'fuel_id': self.parse_fuel(),
            'engine': self.parse_engine(),
            'description': self.parse_description(),
            'mileage': self.parse_mileage(),
            'body_id': self.parse_body(),
            'image': self.parse_image(),
            'dtp': self.parse_dtp(),
            'sold': False,
            'cleared': self.parse_cleared(),
            'olx_link': self.parse_link(),
            'createdAt': self.parse_date_create(),
            'updatedAt': timezone.now(),
            'last_site_updatedAt': None
        }

    def check_time_valid(self, row):
        line = self.xpath(f'//*[@id="offers_table"]/tbody/tr[{row}]/td/div/table/tbody/tr[2]/td[1]/div/p/small[2]/span')
        if line is None:
            return Exception(NoSuchElementException)
        line = line.text
        print(f'Time <{line[line.rfind(" ") + 1:]}> - <{self.last_pars}>')
        if line[line.rfind(' ') + 1:] == self.last_pars:
            print('time is bad')
            return False
        return True

    def stack_links(self):
        self.links_of_post = []
        for row in range(2, 40):
            print(f'row {row}')
            try:
                if self.check_time_valid(row):
                    self.links_of_post.append(
                        self.driver.find_element_by_xpath(
                        f'//*[@id="offers_table"]/tbody/tr[{row}]/td/div/table/tbody/tr[1]/td[2]/div/h3/a').get_attribute(
                        'href'))
                else:
                    return False
            except NoSuchElementException:
                pass
        print('good, stack_links successfully complete')
        return True

    @staticmethod
    def read_start_time():
        with open('./shed_olx.txt', 'r') as file:
            v_time = file.read()
            print(v_time)
        print(f'###################### read time <{v_time}> #####')
        return v_time

    def write_start_time(self):
        line = self.xpath('//*[@id="offers_table"]/tbody/tr[2]/td/div/table/tbody/tr[2]/td[1]/div/p/small[2]/span').text
        time = line[line.rfind(' ') + 1:]
        with open('shed_olx.txt', 'w+') as file:
            file.write(time)

    def set_price(self):
        price = self.parse_price()
        PriceHistory(car=self.car, price=price, date_set=timezone.now(), site='OLX').save()

    def find_same_car(self):
        car_same = find_same_car(self.car_dict, self.car_dict['model_id'], site='olx')
        if car_same:
            print(f'find same car, id={car_same.id}')
            car_same.olx_link = self.driver.current_url
            car_same.updatedAt = timezone.now()
            self.car = car_same
            return
        self.car = Car(**self.car_dict)

    @staticmethod
    def check_car_is_present(link):
        if Car.objects.filter(olx_link=link).first():
            print('car present')
            return True
        return False


class OLXUpdater(ParsDataOLX):
    driver = None
    chrome_options = None
    proxy = {
        'address5': '45.67.120.4:30032',
        'address3': '45.67.120.6:30032',
        'address4': '45.67.123.107:30032',
        'address1': '45.67.123.13:30032',
        'address2': '45.67.120.171:30032',
        'username': 'jorjclub0420_gmail_c',
        'password': '2c752798d6'}

    def __init__(self, list_of_cars: list):
        self.list_of_cars = list_of_cars
        self.set_driver()
        self.run()
        pass

    def set_driver(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.headless = False
        self.chrome_options.add_argument(f'--proxy={self.proxy["address5"]}')
        self.chrome_options.add_argument(f'--proxy-auth={self.proxy["username"]}:{self.proxy["password"]}')
        ua = UserAgent()
        self.chrome_options.add_argument(f'user-agent={ua.random}')
        self.driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=self.chrome_options)
        # chrome_options.binary_location = "/usr/bin/chromium-browser"                                       # for serv
        # self.driver = webdriver.Chrome(executable_path='./chromium_driver', chrome_options=chrome_options) # for serv

    def run(self):
        for car in self.list_of_cars:
            self.driver.get(car.olx_link)
            new_price = self.parse_price()
            if new_price:
                if car.price != new_price:
                    self.


    def set_price(self):
        pass

def update_olx_util():
    cars = Car.objects.filter(sold=False).exclude(olx_link='')
    pages = Paginator(cars, 100)
    OLXUpdater(pages.page(1))
