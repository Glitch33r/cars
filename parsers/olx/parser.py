import logging
from time import sleep
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from main.models import Model, Car, Location, Fuel, Gearbox, Body, Color, SellerPhone


class OLX:
    driver = None

    def __init__(self, url):
        print('Browser opens')
        self.model_db = Model.objects
        self.loc_db = Location.objects
        self.fuel_db = Fuel.objects
        self.gearbox_db = Gearbox.objects
        self.body_db = Body.objects
        self.color_db = Color.objects
        self.seller_db = SellerPhone.objects
        self.url = url
        options = Options()
        options.headless = True
        self.driver = Firefox(executable_path='C:/Users/Dmitry/PycharmProjects/cars/webdriver/geckodriver.exe',
                              options=options)
        self.driver.get(self.url)
        self.driver.implicitly_wait(10)

    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    # logging.getLogger("requests").setLevel(logging.WARNING)

    def _get_user_phone(self):
        try:
            button_spoiler = self.driver.find_element_by_xpath('//div[contains(@class, "contact-button")]/span')
            button_spoiler.click()
            sleep(1.5)
            telephone_number = self.driver.find_element_by_xpath('//div[contains(@class, "contact-button")]/strong')
            result = telephone_number.text.replace(' ', '')
            return self.phone_format(result)
        except:
            return ''

    def _get_price(self):
        price = self.driver.find_element_by_xpath('//div[contains(@class, "price-label")]/strong')
        result = int(price.text.replace('$', '').replace(' ', ''))
        return result

    def _get_user_location(self):
        loc = self.driver.find_element_by_xpath('//*[@id="offerdescription"]/div[2]/div[1]/a/strong')
        result = loc.text.split(',')
        return result[1].strip()

    def _get_car_info(self):
        car = {}
        prop = self.driver.find_elements_by_xpath('//*[@id="offerdescription"]/div[3]/table/tbody/tr/td')
        for p in prop:
            try:
                prop_name = p.find_element_by_css_selector('th').text
                if prop_name == 'Цвет':
                    color = p.find_element_by_css_selector('td.value').text.lowercase()
                    print(color)
                    if not self.color_db.filter(name__contains=color).first():
                        car['color'] = Color(name=color.lowercase()).save()
                    else:
                        car['color'] = self.color_db.filter(name__contains=color.lowercase()).first()
                elif prop_name == 'Год выпуска':
                    car['year'] = int(p.find_element_by_css_selector('td.value').text)
                elif prop_name == 'Тип кузова':
                    body = p.find_element_by_css_selector('td.value').text.lowercase().replace(' ', '')
                    if not self.body_db.filter(name__contains=body).first():
                        car['body'] = Body(name=body).save()
                    else:
                        car['body'] = self.body_db.filter(name__contains=body).first()
                    # car['body'] = body
                elif prop_name == 'Модель':
                    brand_model_url = p.find_element_by_css_selector('td.value strong a').get_attribute(
                        "href").split('/')
                    car['model'] = brand_model_url[-3]
                    # car['model'] = self.model_db.filter(name__contains=model).first()
                    car['brand'] = brand_model_url[-4]
                    # car['brand'] = self.model_db.filter(ma)
                elif prop_name == 'Пробег':
                    car['mileage'] = int(
                        p.find_element_by_css_selector('td.value').text.replace('км', '').replace(' ', ''))
                elif prop_name == 'Коробка передач':
                    gearbox = p.find_element_by_css_selector('td.value').text.lowercase().replace(' ', '')
                    if not self.gearbox_db.filter(name__contains=gearbox).first():
                        car['gearbox'] = Gearbox(name=gearbox).save()
                    else:
                        car['gearbox'] = self.body_db.filter(name__contains=gearbox).first()
                elif prop_name == 'Объем двигателя':
                    car['engine'] = int(
                        p.find_element_by_css_selector('td.value').text.replace('см³', '').replace(' ', '')) / 1000
                elif prop_name == 'Вид топлива':
                    fuel = p.find_element_by_css_selector('td.value').text.lowercase()
                    # car['fuel'] = self.fuel_db.filter(name__contains=fuel.lowercase()).first()
                    if not self.fuel_db.filter(name__contains=fuel).first():
                        car['fuel'] = Fuel(name=fuel).save()
                    else:
                        car['fuel'] = self.body_db.filter(name__contains=fuel).first()
                elif prop_name == 'Растаможена':
                    clear = p.find_element_by_css_selector('td.value').text
                    car['cleared'] = 0 if clear == 'Нет' else 1
            except:
                pass
            car['url'] = self.url

        return car

    def _get_user_name(self):
        try:
            name = self.driver.find_element_by_xpath('//div[contains(@class, "offer-user__details")]/h4/a')
            return name.text.capitalize()
        except:
            name = ''
        return name

    @staticmethod
    def phone_format(phone):
        phone = '38' + phone if phone[0:2] != '38' and phone[0:3] != '+38' else phone
        phone = '+' + phone if phone[0:1] != '+' else phone
        return phone

    def start(self):
        data = dict()
        try:
            cookie = self.driver.find_element_by_xpath('//button[contains(@class, "cookie-close abs cookiesBarClose")]')
            cookie.click()
        except:
            pass

        if self._get_user_phone():
            seller = {
                'seller': {
                    'telephone': self._get_user_phone(),
                    'location': self._get_user_location()
                }
            }
            data.update(seller)
            data.update({'car': self._get_car_info()})

        print(data)
        return data

    def __del__(self):
        print('Browser will be closed')
        self.driver.close()
