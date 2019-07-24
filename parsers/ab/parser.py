"""Parser Autobazar (https://ab.ua/)"""
import json
from datetime import datetime
import requests
from django.db.models import Q
from django.utils.timezone import get_current_timezone


from parsers.utils import get_model_id, find_same_car

from main.models import (
    SellerPhone,
    Car,
    Location,
    PriceHistory,

)
from parsers.choises import GEARBOX, FUEL, BODY, COLOR, LOCATION_ALL

TZ = get_current_timezone()


class Ab:
    """Collects and updates car information from the site https://ab.ua/"""
    url = 'https://ab.ua/api/_posts/'

    def __init__(self):
        pass

    @staticmethod
    def get_formatted_phone(phone):
        """Returns formatted phone number"""
        phone = phone.replace('+', '')
        if len(phone) != 12:
            phone = '380' + phone[-9:]
        return phone

    @staticmethod
    def get_last_site_update(json_data):
        """Returns localized date"""
        if not json_data['date_created']:
            return TZ.localize(datetime.strptime(json_data['hot_date'][0:19], '%Y-%m-%dT%H:%M:%S'))
        return TZ.localize(datetime.strptime(json_data['date_created'][0:19], '%Y-%m-%dT%H:%M:%S'))

    @staticmethod
    def set_price(car, price):
        """Set price history"""
        price = int(price)
        price_history_obj = PriceHistory.objects.filter(car=car, site='AB').first()
        if car.price != price and ((price_history_obj and price_history_obj.price != price) or not price_history_obj):
            PriceHistory.objects.create(car=car, price=price, site='AB')

    def get_seller(self, car_id, dealer):
        """Returns SellerPhone object"""
        url = self.url + '{0}/phones/'
        seller_phones = []

        for phone in json.loads(requests.get(url.format(car_id)).text):
            seller_phones.append(self.get_formatted_phone(phone))

        query = Q()
        for phone in seller_phones:
            query = query | Q(phone__contains=phone)

        seller = SellerPhone.objects.filter(query).first()

        if seller:
            old_phones = seller.phone.split(',')
            phones = set(old_phones + seller_phones)
            seller.phone = ','.join(phones)
            seller.dealer = dealer
            seller.save()
        else:
            phones = ','.join(seller_phones)
            seller = SellerPhone.objects.create(phone=phones, dealer=dealer)
        return seller

    def get_car_ids_by_page(self, page):
        """Returns car_id list on page"""
        url = self.url + '?transport=1&page={0}'
        res = requests.get(url.format(page))
        car_ids = []
        if res.status_code == 200:
            r_json = json.loads(res.text)
            for car in r_json['results']:
                car_ids.append(car['id'])
        else:
            print('{} page not found'.format(page))
        return car_ids

    def get_info_by_id(self, car_id):
        """Returns information about a car by the given car_id"""
        url = self.url + '{0}/'.format(car_id)

        print('Get info from {}'.format(url))

        data = {
            'car_id': car_id,
            'sold': False,
            'dtp': False
        }
        res = requests.get(url)

        if res.status_code == 200:
            json_data = json.loads(res.text)

            data['sold'] = bool(json_data['sold'] or not json_data['active'])

            if not data['sold']:
                data['dtp'] = bool(json_data['is_crashed'])
                data['cleared'] = bool(not json_data['is_not_cleared'])
                data['ab_link'] = 'https://ab.ua' + json_data['permalink']
                data['agency'] = bool(json_data['agency']['id'])
                data['seller'] = self.get_seller(car_id, data['agency'])

                for price in json_data['price']:
                    if price['currency'] == 'usd':
                        data['price'] = int(price['value'])

                data['seller_name'] = json_data['contact_name']

                data['year'] = json_data['year']
                data['mileage'] = json_data['mileage']

                data['engine'] = json_data['characteristics']['capacity']['number'] \
                    if 'capacity' in json_data['characteristics'] else None

                # get mark and model
                mark = json_data['make']['slug'].lower() if json_data['make']['slug'] else None
                model = json_data['model']['slug'].lower() if json_data['model']['slug'] else None
                if mark is not None and model is not None:
                    data['model_id'] = get_model_id(mark, model)
                else:
                    data['model_id'] = None

                # get location
                location = json_data['location']['title'].lower() if json_data['location'] else None
                data['location_id'] = LOCATION_ALL.get(location)

                # get gearbox id
                gearbox = json_data['characteristics']['gearbox']['title'].lower() \
                    if 'gearbox' in json_data['characteristics'] else None
                gearbox = 'ручная/механика' \
                    if gearbox == 'механика' else gearbox
                data['gearbox_id'] = GEARBOX.get(gearbox)

                # get body id
                body = json_data['characteristics']['category']['title'].lower() \
                    if 'category' in json_data['characteristics'] else None
                body = 'внедорожник/кроссовер' if body == 'внедорожник' \
                    or body == 'кроссовер' else body
                body = 'хэтчбек' if body == 'хетчбэк' else body
                body = 'лифтбек' if body == 'лифтбэк' else body
                data['body_id'] = BODY.get(body)

                # get fuel id
                fuel = json_data['characteristics']['engine']['title'][:6].lower() \
                    if 'engine' in json_data['characteristics'] else None
                fuel = fuel + 'о' if fuel == 'электр' else fuel
                fuel = 'газ/бензин' if fuel == 'газ, б' else fuel
                data['fuel_id'] = FUEL.get(fuel)

                # get color id
                color = json_data['color']['title'].lower().replace('ё', 'е') \
                    if json_data['color']['title'] is not None else None
                color = 'золотой' if color == 'золотистый' else color
                color = 'серебряный' if color == 'серебристый' else color
                data['color_id'] = COLOR.get(color)

                data['description'] = json_data['description'] if json_data['description'] else None

                data['image'] = json_data['photos'][0]['image'] if json_data['photos'] else None

                data['last_site_updatedAt'] = self.get_last_site_update(json_data)

        else:
            data['sold'] = True

        return data

    def parse(self, start, finish):
        """Creates Car model objects from inbound page list"""
        for page in range(start, finish):
            print('{} page of {}'.format(page, finish))
            for car_id in self.get_car_ids_by_page(page):
                data = self.get_info_by_id(car_id)

                if not data['sold']:
                    car = Car.objects.filter(ab_link=data['ab_link']).first()
                    if not car and data['model_id']:
                        car = find_same_car(data, data['model_id'], 'ab')
                        if car:
                            print(f' ###########################################')
                            print(f' ##### Car {car.id} exists,add ab_link #####')
                            print(f' ###########################################')
                            car.ab_link = data['ab_link']
                            car.ab_car_id = car_id
                            car.updatedAt = TZ.localize(datetime.now())
                            car.save()
                        else:
                            car = Car.objects.create(
                                model_id=data['model_id'],
                                gearbox_id=data['gearbox_id'],
                                location_id=data['location_id'],
                                fuel_id=data['fuel_id'],
                                color_id=data['color_id'],
                                year=data['year'],
                                mileage=data['mileage'],
                                engine=data['engine'],
                                description=data['description'],
                                seller=data['seller'],
                                body_id=data['body_id'],
                                image=data['image'],
                                dtp=data['dtp'],
                                cleared=data['cleared'],
                                last_site_updatedAt=data['last_site_updatedAt'],
                                updatedAt=TZ.localize(datetime.now()),
                                ab_link=data['ab_link'],
                                ab_car_id=car_id
                            )
                        self.set_price(car, data['price'])

    def update(self, car):
        """Updates existing Car objects"""
        data = self.get_info_by_id(car.ab_car_id)
        if data['sold'] is True:
            car.sold = True
            car.save()
        else:
            self.set_price(car, data['price'])
            if car.last_site_updatedAt != data['last_site_updatedAt']:
                car.last_site_updatedAt = data['last_site_updatedAt']
            car.updatedAt = TZ.localize(datetime.now())
            car.save()
