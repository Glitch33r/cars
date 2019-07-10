"""Parser Autobazar (https://ab.ua/)"""
import json
from datetime import datetime
import requests
from django.db.models import Q
from django.utils.timezone import get_current_timezone

from parsers.utils import GetModel, find_same_car
from main.models import (
    SellerPhone,
    Car,
    Mark,
    Model,
    Location,
    PriceHistory,

)
from parsers.choises import GEARBOX, FUEL, BODY, COLOR

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
                data['location'] = json_data['location']['title'].lower()

                data['mark'] = json_data['make']['slug'].lower() if json_data['make']['slug'] else None
                data['mark_title'] = json_data['make']['title'] \
                    if json_data['make']['title'] else None
                data['model'] = json_data['model']['slug'].lower() if json_data['model']['slug'] else None
                data['model_title'] = json_data['model']['title'] \
                    if json_data['model']['title'] else None

                data['year'] = json_data['year']
                data['mileage'] = json_data['mileage']

                data['engine'] = json_data['characteristics']['capacity']['number'] \
                    if 'capacity' in json_data['characteristics'] else None
                data['gearbox'] = json_data['characteristics']['gearbox']['title'].lower() \
                    if 'gearbox' in json_data['characteristics'] else None
                data['gearbox'] = 'ручная/механика' \
                    if data['gearbox'] == 'механика' else data['gearbox']

                data['body'] = json_data['characteristics']['category']['title'].lower() \
                    if 'category' in json_data['characteristics'] else None
                data['body'] = 'внедорожник/кроссовер' if data['body'] == 'внедорожник' \
                    or data['body'] == 'кроссовер' else data['body']
                data['body'] = 'хэтчбек' if data['body'] == 'хетчбэк' else data['body']
                data['body'] = 'лифтбек' if data['body'] == 'лифтбэк' else data['body']

                data['fuel'] = json_data['characteristics']['engine']['title'][:6].lower() \
                    if 'engine' in json_data['characteristics'] else None
                data['fuel'] = data['fuel'] + 'о' if data['fuel'] == 'электр' else data['fuel']
                data['fuel'] = 'газ/бензин' if data['fuel'] == 'газ, б' else data['fuel']

                data['color'] = json_data['color']['title'].lower().replace('ё', 'е') \
                    if json_data['color']['title'] is not None else None
                data['color'] = 'золотой' if data['color'] == 'золотистый' else data['color']
                data['color'] = 'серебряный' if data['color'] == 'серебристый' else data['color']

                data['description'] = json_data['description']

                data['image'] = json_data['photos'][0]['image'] if json_data['photos'] else None

                data['last_site_updatedAt'] = self.get_last_site_update(json_data)

        else:
            data['sold'] = True

        return data

    def parse(self, start, finish):
        """Creates Car model objects from inbound page list"""
        for page in range(start, finish + 1):
            print('{} page of {}'.format(page, finish))
            for car_id in self.get_car_ids_by_page(page):
                data = self.get_info_by_id(car_id)

                car = Car.objects.filter(ab_link=data['ab_link']).first()

                if not car:
                    # if data['mark'] is None:
                    #     mark = None
                    # else:
                    #     mark = Mark.objects.filter(eng=data['mark']).first()
                    #     if not mark:
                    #         mark = Mark.objects.create(eng=data['mark'], name=data['mark_title'])

                    # if data['model'] is None:
                    #     model = None
                    # else:
                    #     model = Model.objects.filter(eng=data['model'], mark=mark).first()
                    #     if not model:
                    #         model = Model.objects.create(
                    #             eng=data['model'],
                    #             name=data['model_title'],
                    #             mark=mark)

                    if data['mark'] is not None and data['model'] is not None:
                        obj = GetModel(data['mark'], data['model'])
                        model_id = obj.get_model_id()
                    else:
                        model_id = None

                    location = Location.objects.filter(name=data['location']).first()
                    if not location:
                        location = Location.objects.create(name=data['location'])

                    if model_id:
                        # car = find_same_car(data, model_id)
                        car = Car.objects.filter(
                            model_id=model_id,
                            # gearbox_id=GEARBOX.get(data['gearbox']),
                            # fuel_id=FUEL.get(data['fuel']),
                            # year=data['year'],
                            # mileage=data['mileage'],
                            # engine=data['engine'],
                            seller=data['seller'],
                            # body_id=BODY.get(data['body']),
                            # dtp=data['dtp'],
                            # cleared=data['cleared'],
                            ab_link=''
                        ).first()

                        if car:
                            print(f' ###########################################')
                            print(f' ######car is find {car.id}############')
                            print(f' ###########################################')
                            car.ab_link = data['ab_link']
                            car.ab_car_id = car_id
                            car.updatedAt = TZ.localize(datetime.now())
                            car.save()
                            print('Car exists, add ab_link')
                        else:
                            car = Car.objects.create(
                                model_id=model_id,
                                gearbox_id=GEARBOX.get(data['gearbox']),
                                location=location,
                                fuel_id=FUEL.get(data['fuel']),
                                color_id=COLOR.get(data['color']),
                                year=data['year'],
                                mileage=data['mileage'],
                                engine=data['engine'],
                                description=data['description'],
                                seller=data['seller'],
                                body_id=BODY.get(data['body']),
                                image=data['image'],
                                dtp=data['dtp'],
                                cleared=data['cleared'],
                                last_site_updatedAt=data['last_site_updatedAt'],
                                updatedAt=TZ.localize(datetime.now()),
                                ab_link=data['ab_link'],
                                ab_car_id=car_id
                            )
                        PriceHistory.objects.create(car=car, price=data['price'], site='AB')
        return print('FINISHED')

    def update(self, car):
        """Updates existing Car objects"""
        data = self.get_info_by_id(car.ab_car_id)
        if data['sold'] is True:
            car.sold = True
            car.save()
            print('Car sold')
        else:
            if car.price != data['price']:
                PriceHistory.objects.create(car=car, price=data['price'], site='AB')
            if car.last_site_updatedAt != data['last_site_updatedAt']:
                car.last_site_updatedAt = data['last_site_updatedAt']
            car.updatedAt = TZ.localize(datetime.now())
            car.save()
            print('Car updated')
        return
