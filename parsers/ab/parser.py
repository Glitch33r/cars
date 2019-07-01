import requests
import json
import random
import string
import threading
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

    def __init__(self):
        pages = self.get_count_pages()
        print(pages)
        self.data_record(1, pages)
        # t1 = threading.Thread(target=self.data_record, args=(1, 125))
        # t2 = threading.Thread(target=self.data_record, args=(126, 250))
        # t3 = threading.Thread(target=self.data_record, args=(251, 375))
        # t4 = threading.Thread(target=self.data_record, args=(376, 500))
        # t1.start()
        # t2.start()
        # t3.start()
        # t4.start()
        # t1.join()
        # t2.join()
        # t3.join()
        # t4.join()

    def get_count_pages(self):
        url = 'https://ab.ua/api/_posts/?transport=1'
        r = requests.get(url)
        data = json.loads(r.text)
        return round(data['count'] / 20)

    def get_ids_by_page(self, page):
        url = 'https://ab.ua/api/_posts/?transport=1&page={0}'
        print(url.format(page))
        r = requests.get(url.format(page))
        try:
            r_json = json.loads(r.text)
        except:
            print(r.text, r.status_code)
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
                data['phone'] = ','.join(data['seller_phones'])

                for price in json_data['price']:
                    if price['currency'] == 'usd':
                        data['price'] = int(price['value'])

                data['seller_name'] = json_data['contact_name']
                data['location'] = json_data['location']['title']

                data['mark'] = json_data['make']['slug'] if json_data['make']['title'] else None
                data['mark_title'] = json_data['make']['title'] if json_data['make']['title'] else None
                data['model'] = json_data['model']['slug'] if json_data['model']['title'] else None
                data['model_title'] = json_data['model']['title'] if json_data['model']['title'] else None

                data['year'] = json_data['year']
                data['mileage'] = json_data['mileage']

                data['engine'] = json_data['characteristics']['capacity']['number'] if 'capacity' in json_data['characteristics'] else None
                data['gearbox'] = json_data['characteristics']['gearbox']['title'] if 'gearbox' in json_data['characteristics'] else None
                data['body'] = json_data['characteristics']['category']['title'].lower() if 'category' in json_data['characteristics'] else None
                data['fuel'] = json_data['characteristics']['engine']['title'][:6].lower() if 'engine' in json_data['characteristics'] else None

                if data['fuel']:
                    data['fuel'] = data['fuel'] if data['fuel'] != 'электр' else data['fuel'] + 'о'

                data['color'] = json_data['color']['title'] if json_data['color']['title'] is not None else None
                data['description'] = json_data['description']

                data['images'] = []
                for img in json_data['photos']:
                    data['images'].append(img['image'])
                    data['image'] = img['image']

                data['last_site_updatedAt'] = tz.localize(datetime.strptime(json_data['date_publicated'][0:19].translate(OD), '%Y%m%d%H%M%S'))

        else:
            print('{} SOLD'.format(car_id))

        return data

    def data_record(self, start, finish):
        
        for page in range(start, finish + 1):
            print('get {} page'.format(page))
            for car_id in self.get_ids_by_page(page):
                data = self.get_info_by_id(car_id)

                if data['mark'] is None:
                    mark = None
                else:
                    mark = Mark.objects.filter(eng=data['mark']).first()
                    if not mark:
                        mark = Mark.objects.create(eng=data['mark'], name=data['mark_title'])
                print('*'*20)
                print(data['mark'])
                print(data['mark_title'])
                print('*'*20)
                if data['model'] is None:
                    model = None
                else:
                    print('*'*20)
                    print(data['model'])
                    print('mark - {}'.format(mark))
                    model = Model.objects.filter(eng=data['model'], mark=mark).first()
                    if not model:
                        print('create model eng={}, name={}, mark={}'.format(data['model'],data['model_title'], mark))
                        try:
                            model = Model.objects.create(eng=data['model'], name=data['model_title'], mark=mark)
                        except:
                            print('error')
                            return

                if data['gearbox'] is None:
                    gearbox = None
                else:
                    gearbox = Gearbox.objects.filter(name=data['gearbox']).first()
                    if not gearbox:
                        gearbox = Gearbox.objects.create(name=data['gearbox'])

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

                seller = SellerPhone.objects.filter(phone=data['phone']).first()
                if not seller:
                    seller = SellerPhone.objects.create(phone=data['phone'])

                car = Car.objects.filter(
                    model=model,
                    fuel=fuel,
                    year=data['year'],
                    dtp=data['dtp'],
                    mileage=data['mileage']
                )
                if car:
                    print('CAR IS FINDED')
                else:
                    print('Finish obj')

                # car = Car.objects.filter(ab_link=data['ab_link']).first()
                # if car:
                #     if car.pricehistory_set.filter(price=data['price']):
                #         PriceHistory.objects.create(car=car, price=data['price'])
                #     car.updatedAt = tz.localize(datetime.now())
                #     car.last_site_updatedAt = data['last_site_updatedAt']
                #     car.save()
                #     print('>>>This link exists, the price is updated')
                # # else:
                # #     car = Car.objects.filter(model=model,
                # #                     gearbox=gearbox,
                # #                     fuel=fuel,
                # #                     year=data['year'],
                # #                     mileage=data['mileage'],
                # #                     engine=data['engine'],
                # #                     body=body,
                # #                     dtp=data['dtp']
                # #                     ).first()
                # #     if car:
                # #         car.price = data['price']
                # #         car.ab_link = data['ab_link']
                # #         car.updatedAt = tz.localize(datetime.now())
                # #         car.last_site_updatedAt = data['last_site_updatedAt']
                # #         car.save()
                # #         print('Updated')

                # else:
                #     car = Car(
                #         model=model,
                #         gearbox=gearbox,
                #         location=location,
                #         fuel=fuel,
                #         color=color,
                #         year=data['year'],
                #         mileage=data['mileage'],
                #         engine=data['engine'],
                #         description=data['description'],
                #         phone=seller,
                #         body=body,
                #         image=data['image'],
                #         dtp=data['dtp'],
                #         createdAt=tz.localize(datetime.now()),
                #         updatedAt=tz.localize(datetime.now()),
                #         last_site_updatedAt=data['last_site_updatedAt'],
                #         ab_link=data['ab_link']
                #     )
                #     car.save()
                #     PriceHistory.objects.create(car=car, price=data['price'])
                #     print('Object created')
        return print('FINISHED')
