import requests
import json
import random
import string
from time import sleep
from datetime import datetime

from main.models import *

from django.utils.timezone import get_current_timezone
tz = get_current_timezone()


# Оставляет в строке только цифры
class DigitsMixin:
    def __init__(self, keep=string.digits):
        self.comp = dict((ord(c),c) for c in keep)
    def __getitem__(self, k):
        return self.comp.get(k)

OD = DigitsMixin()


class Ab:

    def get_count_pages(self):
        url = 'https://ab.ua/api/_posts/?transport=1'
        r = requests.get(url)
        data = json.loads(r.text)
        return data['count']

    def get_ids_by_page(self, page):
        url = 'https://ab.ua/api/_posts/?transport=1&page={0}'
        r = requests.get(url.format(page))
        r_json = json.loads(r.text)
        ids = []
        for auto in r_json['results']:
            ids.append(auto['id'])
        return ids

    def get_info_by_id(self, car_id):
        url = 'https://ab.ua/api/_posts/{0}/'.format(car_id)

        print('Start parsing {}'.format(url))

        data = {
            'car_id': car_id,
            'sold': False,
            'dtp': False
        }
        r = requests.get(url)

        if r.status_code == 404:
            data['sold'] = True

        if not data['sold']:
            json_data = json.loads(r.text)

            data['sold'] = True if json_data['sold'] or not json_data['active'] else False
            data['dtp'] = True if json_data['is_crashed'] else False
            data['ab_link'] = 'https://ab.ua' + json_data['permalink']

            if not data['sold']:
                data['seller_phones'] = []
                for phone in json.loads(requests.get("https://ab.ua/api/_posts/{0}/phones/".format(car_id)).text):
                    data['seller_phones'].append(phone)
                    data['phone'] = phone

            for price in json_data['price']:
                if price['currency'] == 'usd':
                    data['price'] = int(price['value'])

            data['seller_name'] = json_data['contact_name']
            data['location'] = json_data['location']['title']

            data['mark'] = json_data['make']['title'].lower()
            data['model'] = json_data['model']['title'].lower()

            data['year'] = json_data['year']
            data['mileage'] = int(json_data['mileage'] * 1000)

            data['engine'] = json_data['characteristics']['capacity']['number'] if 'capacity' in json_data['characteristics'] else None
            data['gearbox'] = json_data['characteristics']['gearbox']['title'] if 'gearbox' in json_data['characteristics'] else None
            data['body'] = json_data['characteristics']['category']['title'] if 'category' in json_data['characteristics'] else None
            data['fuel'] = json_data['characteristics']['engine']['title'][:6].lower() if 'engine' in json_data['characteristics'] else None

            if data['fuel']:
                data['fuel'] = data['fuel'] if data['fuel'] != 'электр' else data['fuel'] + 'о'

            data['color'] = json_data['color']['title'] if json_data['color']['title'] is not None else ''
            data['description'] = json_data['description']

            data['images'] = []
            for img in json_data['photos']:
                data['images'].append(img['image'])
                data['image'] = img['image']

            data['last_site_updatedAt'] = tz.localize(datetime.strptime(json_data['date_publicated'][0:19].translate(OD), '%Y%m%d%H%M%S'))

        else:
            print('{} SOLD'.format(car_id))

        return data

    def data_record(self):
        
        pages = self.get_count_pages()
        for page in range(1, 5):
            print('get {} page'.format(page))
            sleep(random.randint(5, 10))
            for car_id in self.get_ids_by_page(page):
                sleep(random.randint(3, 5))
                data = self.get_info_by_id(car_id)

                try:
                    phone = SellerPhone.objects.get(phone=data['phone'])
                except:
                    SellerPhone.objects.create(phone=data['phone'])
                    phone = SellerPhone.objects.get(phone=data['phone'])

                try:
                    mark = Mark.objects.get(name=data['mark'])
                except:
                    Mark.objects.create(name=data['mark'])
                    mark = Mark.objects.get(name=data['mark'])

                try:
                    model = Model.objects.get(name=data['model'])
                except:
                    Model.objects.create(name=data['model'], mark=mark)
                    model = Model.objects.get(name=data['model'])

                if data['gearbox'] is None:
                    gearbox = None
                else:
                    try:
                        gearbox = Gearbox.objects.get(name=data['gearbox'])
                    except:
                        Gearbox.objects.create(name=data['gearbox'])
                        gearbox = Gearbox.objects.get(name=data['gearbox'])

                try:
                    location = Location.objects.get(name=data['location'])
                except:
                    Location.objects.create(name=data['location'])
                    location = Location.objects.get(name=data['location'])

                if data['fuel'] is None:
                    fuel = None
                else:
                    try:
                        fuel = Fuel.objects.get(name=data['fuel'])
                    except:
                        Fuel.objects.create(name=data['fuel'])
                        fuel = Fuel.objects.get(name=data['fuel'])

                try:
                    color = Color.objects.get(name=data['color'])
                except:
                    Color.objects.create(name=data['color'])
                    color = Color.objects.get(name=data['color'])

                if data['body'] is None:
                    body = None
                else:
                    try:
                        body = Body.objects.get(name=data['body'])
                    except:
                        Body.objects.create(name=data['body'])
                        body = Body.objects.get(name=data['body'])

                try:
                    try:
                        car = Car.objects.get(ab_link=data['ab_link'])
                        car.price = data['price']
                        car.updatedAt = tz.localize(datetime.now())
                        car.last_site_updatedAt = data['last_site_updatedAt']
                        car.save()
                        print('Price updated')
                    except:
                        car = Car.objects.get(model=model,
                                        gearbox=gearbox,
                                        location=location,
                                        fuel=fuel,
                                        color=color,
                                        year=data['year'],
                                        mileage=data['mileage'],
                                        engine=data['engine'],
                                        body=body,
                                        dtp=data['dtp']
                                        )
                        car.price = data['price']
                        car.ab_link = data['ab_link']
                        car.updatedAt = tz.localize(datetime.now())
                        car.last_site_updatedAt = data['last_site_updatedAt']
                        car.phone = phone
                        car.save()
                        print('Updated')
                except:
                    car = Car.objects.create(model=model,
                                        gearbox=gearbox,
                                        location=location,
                                        fuel=fuel,
                                        color=color,
                                        year=data['year'],
                                        mileage=data['mileage'],
                                        engine=data['engine'],
                                        description=data['description'],
                                        price=data['price'],
                                        phone=phone,
                                        body=body,
                                        image=data['image'],
                                        dtp=data['dtp'],
                                        createdAt=tz.localize(datetime.now()),
                                        last_site_updatedAt=data['last_site_updatedAt'],
                                        ab_link=data['ab_link']
                                        )
                    car.save()
                    print('Object created')
        return print('FINISHED')
