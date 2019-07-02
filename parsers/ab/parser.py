import requests
import json
import random
import string
import threading
from time import sleep
from datetime import datetime
from django.db.models import Q
from django.utils.timezone import get_current_timezone

from main.models import *
from parsers.choises import gearbox

tz = get_current_timezone()


class Ab:

    def __init__(self):
        # pages = self.get_count_pages()
        # self.parse(1, pages)
        t1 = threading.Thread(target=self.parse, args=(1, 250))
        t2 = threading.Thread(target=self.parse, args=(251, 500))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    @staticmethod
    def get_formatted_phone(phone):
        phone = phone.replace('+', '')
        if len(phone) != 12:
            phone = '380' + phone[-9:]
        return phone

    @staticmethod
    def get_last_site_update(json_data):
        if not json_data['date_created']:
            return tz.localize(datetime.strptime(json_data['hot_date'][0:19], '%Y-%m-%dT%H:%M:%S'))
        return tz.localize(datetime.strptime(json_data['date_created'][0:19], '%Y-%m-%dT%H:%M:%S'))

    def get_seller(self, car_id):
        seller_phones = []
        for phone in json.loads(requests.get("https://ab.ua/api/_posts/{0}/phones/".format(car_id)).text):
            seller_phones.append(self.get_formatted_phone(phone))

        query = Q()
        phones = ''
        for phone in seller_phones:
            phones += phone + ','
            query = query | Q(phone__contains=phone)

        seller = SellerPhone.objects.filter(query).first()
        if seller:
            for phone in seller_phones:
                if phone not in seller.phone:
                    seller.phone += phone + ','
                    seller.save()
        else:
            seller = SellerPhone.objects.create(phone=phones)
        return seller

    def get_count_pages(self):
        url = 'https://ab.ua/api/_posts/?transport=1'
        r = requests.get(url)
        data = json.loads(r.text)
        return round(data['count'] / 20)

    def get_car_ids_by_page(self, page):
        url = 'https://ab.ua/api/_posts/?transport=1&page={0}'
        r = requests.get(url.format(page))
        car_ids = []
        if r.status_code == 200:
            r_json = json.loads(r.text)
            for car in r_json['results']:
                car_ids.append(car['id'])
        else:
            print('{} page not found'.format(page))
        return car_ids

    def get_info_by_id(self, car_id):
        url = 'https://ab.ua/api/_posts/{0}/'.format(car_id)

        print('Parsing {}'.format(url))

        data = {
            'car_id': car_id,
            'sold': False,
            'dtp': False
        }
        r = requests.get(url)

        if r.status_code == 200:
            json_data = json.loads(r.text)

            data['sold'] = True if json_data['sold'] or not json_data['active'] else False
            data['dtp'] = True if json_data['is_crashed'] else False
            data['ab_link'] = 'https://ab.ua' + json_data['permalink']

            if not data['sold']:
                data['seller'] = self.get_seller(car_id)

                for price in json_data['price']:
                    if price['currency'] == 'usd':
                        data['price'] = int(price['value'])

                data['seller_name'] = json_data['contact_name']
                data['location'] = json_data['location']['title'].lower()

                data['mark'] = json_data['make']['slug'] if json_data['make']['title'] else None
                data['mark_title'] = json_data['make']['title'] if json_data['make']['title'] else None
                data['model'] = json_data['model']['slug'] if json_data['model']['title'] else None
                data['model_title'] = json_data['model']['title'] if json_data['model']['title'] else None

                data['year'] = json_data['year']
                data['mileage'] = json_data['mileage']

                data['engine'] = json_data['characteristics']['capacity']['number'] if 'capacity' in json_data['characteristics'] else None
                data['gearbox'] = json_data['characteristics']['gearbox']['title'].lower() if 'gearbox' in json_data['characteristics'] else None
                data['gearbox'] = 'ручная/механика' if data['gearbox'] == 'механика' else data['gearbox']
                data['body'] = json_data['characteristics']['category']['title'].lower() if 'category' in json_data['characteristics'] else None
                data['fuel'] = json_data['characteristics']['engine']['title'][:6].lower() if 'engine' in json_data['characteristics'] else None

                if data['fuel']:
                    data['fuel'] = data['fuel'] if data['fuel'] != 'электр' else data['fuel'] + 'о'

                data['color'] = json_data['color']['title'] if json_data['color']['title'] is not None else None
                data['description'] = json_data['description']

                data['image'] = json_data['photos'][0]['image'] if json_data['photos'] else None

                data['last_site_updatedAt'] = self.get_last_site_update(json_data)

        else:
            data['sold'] = True

        return data

    def parse(self, start, finish):

        for page in range(start, finish + 1):
            print('{} page of {}'.format(page, finish))
            for car_id in self.get_car_ids_by_page(page):
                data = self.get_info_by_id(car_id)

                car = Car.objects.filter(ab_link=data['ab_link']).first()

                if not car:
                    if data['mark'] is None:
                        mark = None
                    else:
                        mark = Mark.objects.filter(eng=data['mark']).first()
                        if not mark:
                            mark = Mark.objects.create(eng=data['mark'], name=data['mark_title'])

                    if data['model'] is None:
                        model = None
                    else:
                        model = Model.objects.filter(eng=data['model'], mark=mark).first()
                        if not model:
                            model = Model.objects.create(eng=data['model'], name=data['model_title'], mark=mark)

                    location = Location.objects.filter(name=data['location']).first()
                    if not location:
                        location = Location.objects.create(name=data['location'])

                    if data['fuel'] is None:
                        fuel = None
                    else:
                        fuel = Fuel.objects.filter(name=data['fuel']).first()
                        if not fuel:
                            fuel = Fuel.objects.create(name=data['fuel'])

                    if data['color'] is None:
                        color = None
                    else:
                        color = Color.objects.filter(name=data['color']).first()
                        if not color:
                            color = Color.objects.create(name=data['color'])

                    if data['body'] is None:
                        body = None
                    else:
                        body = Body.objects.filter(name=data['body']).first()
                        if not body:
                            body = Body.objects.create(name=data['body'])

                    car = Car(
                        model=model,
                        gearbox_id=gearbox.get(data['gearbox']),
                        location=location,
                        fuel=fuel,
                        color=color,
                        year=data['year'],
                        mileage=data['mileage'],
                        engine=data['engine'],
                        description=data['description'],
                        phone=data['seller'],
                        body=body,
                        image=data['image'],
                        dtp=data['dtp'],
                        last_site_updatedAt=data['last_site_updatedAt'],
                        ab_link=data['ab_link'],
                        ab_car_id=car_id
                    )
                    car.save()
                    PriceHistory.objects.create(car=car, price=data['price'])
                #     print('Object created')

                # else:
                #     print('Car exists')
        return print('FINISHED')

    def update(self, car_id):
        car = Car.objects.filter(ab_car_id=car_id).first()
        if car:
            data = self.get_info_by_id(car_id)
            if data['sold'] == True:
                car.sold = True
                car.save()
            else:
                pass
                #     if car.price != data['price']:
                #         PriceHistory.objects.create(car=car, price=data['price'])
                #     car.updatedAt = tz.localize(datetime.now())
                #     car.last_site_updatedAt = data['last_site_updatedAt']
                #     car.save()
                #     print('>>>This link exists, the price is updated')
