import datetime
import json
import time
import threading
from django.utils import timezone
from django.utils.timezone import get_current_timezone
import requests

from main.models import Model, Car, SellerPhone, PriceHistory
from parsers.choises import location, fuel, gearbox

tz = get_current_timezone()


class WordsFormater:

    def engine_parse(self, word: str):
        if word == 'Не указано':
            return None
        elif word.find(', ') == -1:
            return None
        return float(word[word.find(', ') + 1:word.find('л.')])

    def fuel_parse(self, word: str):
        return word[:word.find(',')].lower()

    def formating(self, word: str):
        return word.lower().replace(' ', '')

    def format_phone(self, word: str):
        integers = '0123456789'
        response = word
        for liter in word:
            if liter not in integers:
                response = response.replace(liter, '')
        if response[:3] == '380':
            return response[2:]
        return response

    def check_dtp(self, word: str):
        exept = 'После ДТП'
        if exept in word:
            return True
        return False

    def format_date(self, word: str):
        if len(word) <= 10:
            return None
        return tz.localize(datetime.datetime.strptime(word, '%Y-%m-%d %H:%M:%S'))


class AutoRiaInnerParse(WordsFormater):
    list_posts_way = 'http://auto.ria.com/blocks_search_ajax/search/?countpage={}&category_id=1&page={}&saledParam=2'
    post_way = 'https://auto.ria.com/demo/bu/searchPage/v2/view/auto/{}/?lang_id=2'

    def __init__(self):
        print('Hi, I\'m started')
        self.first_data = json.loads(requests.get(self.list_posts_way.format(10, 0)).content)
        print(self.first_data['result']['search_result']['count'] // 100)
        t1 = threading.Thread(target=self.runner, args=(0, 500))
        t2 = threading.Thread(target=self.runner, args=(501, 1000))
        t3 = threading.Thread(target=self.runner, args=(1001, 1500))
        t4 = threading.Thread(target=self.runner, args=(1501, self.first_data['result']['search_result']['count'] // 100))
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()

    def set_saller(self, phone):
        saller = SellerPhone.objects.filter(phone=self.format_phone(phone)).first()
        if saller:
            return saller
        saller = SellerPhone(phone=self.format_phone(phone))
        saller.save()
        return saller

    def find_model(self, data: dict):
        model = Model.objects.filter(
            ria_id=data['modelId'], mark__ria_id=data['markId']).first()
        if not model:
            return None
        return model

    def set_price(self, price_int: int, car):
        print(price_int)
        price = PriceHistory(price=price_int, date_set=timezone.now(), car=car)
        price.save()
        print(price)

    def set_car(self, data: dict):
        car = Car(model=self.find_model(data),
                  gearbox_id=gearbox.get(self.formating(data['autoData']['gearboxName'])),
                  location_id=location.get(self.formating(data['stateData']['regionName'])),
                  fuel_id=fuel.get(self.fuel_parse(data['autoData']['fuelName'])),
                  engine=self.engine_parse(data['autoData']['fuelName']),
                  color=None,
                  year=data['autoData']['year'],
                  mileage=data['autoData']['raceInt'],
                  # price=self.set_price(data['USD']),
                  phone=self.set_saller(data['userPhoneData']['phone']),
                  body_id=data['autoData'].get('bodyId'),
                  image=data['photoData']['seoLinkF'],
                  dtp=self.check_dtp(data['infoBarText']),
                  sold=data['autoData']['isSold'],
                  cleared=not bool(data['autoData']['custom']),
                  ria_link='https://auto.ria.com' + data['linkToView'],
                  createdAt=self.format_date(data['addDate']),
                  updatedAt=timezone.now(),
                  last_site_updatedAt=self.format_date(data['updateDate'])
                  )
        return car

    def runner(self, start, finish):
        for i in range(start, finish):
            print('####', i)
            if i > 900:
                return
            start_data = json.loads(requests.get(self.list_posts_way.format(100, i)).content)
            for ids in start_data['result']['search_result']['ids']:
                try:
                    data = json.loads(requests.get(self.post_way.format(ids)).content)
                except json.decoder.JSONDecodeError:
                    time.sleep(1)
                    data = json.loads(requests.get(self.post_way.format(ids)).content)
                car = self.set_car(data)
                if car.model:
                    print('car save()')
                    car.save()
                    self.set_price(data['USD'], car)
                else:
                    print(f'car not save Mark:{data["markNameEng"]}, model:{data["modelNameEng"]}, link: https://auto.ria.com{data["linkToView"]}')
                    pass


class AutoRiaUpdateParse(AutoRiaInnerParse):
    list_posts_way = 'http://auto.ria.com/blocks_search_ajax/search/?countpage={}&category_id=1&page={}'
    post_way = 'https://auto.ria.com/demo/bu/searchPage/v2/view/auto/{}/?lang_id=2'

    def __init__(self):
        # count = 0
        first_data = json.loads(requests.get(self.list_posts_way.format(10, 0)).content)
        print(first_data['result']['search_result']['count'] // 100)
        t1 = threading.Thread(target=self.runner, args=(0, 500))
        t2 = threading.Thread(target=self.runner, args=(501, 1000))
        t3 = threading.Thread(target=self.runner, args=(1001, 1500))
        t4 = threading.Thread(target=self.runner, args=(1501, first_data['result']['search_result']['count'] // 100))
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()

    def time_stack(self, updated: str):
        updated = tz.localize(datetime.datetime.strptime(updated, '%Y-%m-%d %H:%M:%S'))
        start = timezone.now() - timezone.timedelta(hours=2)
        print(start, updated, timezone.now())
        updated = updated.timestamp()
        if updated > start.timestamp() and updated < timezone.now().timestamp():
            return True
        return False

    def Noner(self):
        pass

    def runner(self, start, finish):
        count = 0
        for i in range(start, finish):
            print('####', i)
            start_data = json.loads(requests.get(self.list_posts_way.format(100, i)).content)
            for ids in start_data['result']['search_result']['ids']:
                if count > 10900:
                    return
                count += 1
                print(count)
                data = json.loads(requests.get(self.post_way.format(ids)).content)
                if self.time_stack(data['updateDate']):
                    print('good')
                    car = Car.objects.filter(ria_link='https://auto.ria.com' + data['linkToView']).first()
                    if data['autoData']['isSold']:
                        (car.delete, self.Noner,)[bool(car)]()
                        print(f'delete car {data["linkToView"]}')
                    else:
                        print('go to <else:> where car is not sold')
                        model = self.find_model(data)
                        if model:
                            print('model find')
                            if car:
                                print(f'updates price {data["USD"]}')
                                self.set_price(price_int=data['USD'], car=car)
                            else:
                                print('create car')
                                car = self.set_car(data)
                                car.save()
                                self.set_price(price_int=data['USD'], car=car)
                        else:
                            print('model not find')
                            pass
                else:
                    pass


# pass


# {'EUR': 11247,
#  'UAH': 336296,
#  'USD': 12700,
#  'addDate': '2019-06-09 17:17:04',
#  'auctionPossible': True,
#  'autoData': {'active': False,
#               'autoId': 24490777,
#               'bodyId': 2,
#               'categoryId': 1,
#               'categoryNameEng': 'legkovie',
#               'custom': 0,
#               'description': 'Кому нужен идеальный автомобиль, звоните! '
#                              'Renault MEGANE 1.6 MEGANE *BOSE*2014 FACELIFT '
#                              'СВЕЖЕзагнан в Украину. Авто в отличном '
#                              'состоянии. 100% НЕ КРАШЕНА НИ ОДНА ДЕТАЛЬ. '
#                              'РЕАЛЬНЫЙ ПРОБЕГ!!!! ИНДИВИДУАЛЬНАЯ комплектация: '
#                              'Подогрев сидений, Раздельный климат контроль, '
#                              'Круиз контроль,Полный электропакет, Подогрев '
#                              'зеркал и стекол, Задние парктроники, Функция '
#                              'свободные руки, Линзы, Передние и задние '
#                              'противотуманные фонари, Салон с кожаными '
#                              'вставками, Аудио система ВОSE, Электроручник, '
#                              'Старт-стопная система, Отчет расхода топлива, '
#                              'Очень экономная- средний расход 4,6л., 6-ти '
#                              'ступка 96квт. 131л.с. V- 1,6., Подключение тел. '
#                              'по блютуз, Громкая связь, Вазможность слушать '
#                              'музику из интернета, Отличная акустика - 6 '
#                              'динамиков, Русскоязычная навигация, AUX-вход, '
#                              'слот для карт памяти, резина летняя 100% '
#                              'мишелин, Диски на 17", заводская тонировка.',
#               'fromArchive': False,
#               'fuelName': 'Дизель, 1.6 л.',
#               'fuelNameEng': 'dizel',
#               'gearboxName': 'Ручная / Механика',
#               'isSold': True,
#               'mainCurrency': 'USD',
#               'onModeration': False,
#               'race': '140 тыс. км',
#               'raceInt': 140,
#               'statusId': 1,
#               'subCategoryNameEng': 'universal',
#               'version': ' *Bose*',
#               'withVideo': True,
#               'year': 2015},
#  'badges': [],
#  'canSetSpecificPhoneToAdvert': False,
#  'checkedVin': {'checkDate': '12.06.2019',
#                 'hasRestrictions': False,
#                 'isChecked': False,
#                 'isShow': False,
#                 'linkToReport': '/vin-check/auto/24490777/',
#                 'vin': 'VF1KZNA0х50хххх65'},
#  'chipsCount': 0,
#  'cityLocative': 'Борисполе',
#  'dealer': {'id': 0,
#             'link': '',
#             'logo': '',
#             'name': '',
#             'packageId': 0,
#             'type': '',
#             'typeId': 0},
#  'dontComment': 1,
#  'exchangePossible': False,
#  'exchangeType': 'Любой',
#  'exchangeTypeId': 0,
#  'expireDate': '2019-07-09 17:17:04',
#  'hasWebP': 2,
#  'infoBarText': '',
#  'isAutoAddedByPartner': False,
#  'isLeasing': 0,
#  'levelData': {'expireDate': '2019-06-12 17:22:08',
#                'hotType': '',
#                'label': 0,
#                'level': 103},
#  'linkToView': '/auto_renault_megane_24490777.html',
#  'locationCityName': 'Борисполь',
#  'markId': 62,
#  'markName': 'Renault',
#  'markNameEng': 'renault',
#  'modelId': 586,
#  'modelName': 'Megane',
#  'modelNameEng': 'megane',
#  'moderatedAbroad': False,
#  'oldTop': {'expireDate': '', 'isActive': False},
#  'optionStyles': [],
#  'partnerId': 0,
#  'photoData': {'count': 97,
#                'seoLinkB': 'https://cdn1.riastatic.com/photosnew/auto/photo/renault_megane__281200166b.jpg',
#                'seoLinkF': 'https://cdn1.riastatic.com/photosnew/auto/photo/renault_megane__281200166f.jpg',
#                'seoLinkM': 'https://cdn1.riastatic.com/photosnew/auto/photo/renault_megane__281200166m.jpg',
#                'seoLinkSX': 'https://cdn1.riastatic.com/photosnew/auto/photo/renault_megane__281200166sx.jpg'},
#  'realtyExchange': False,
#  'secureKey': 'b1ebf1930f92671427e4eddaea251dbd',
#  'sendComments': 0,
#  'soldDate': '2019-06-11 15:36:49',
#  'stateData': {'cityId': 212,
#                'linkToCatalog': '/city/borispol/',
#                'name': 'Киев',
#                'regionName': 'Киевская',
#                'regionNameEng': 'kiev',
#                'stateId': 10,
#                'title': 'Поиск объявлений по городу Борисполь'},
#  'title': 'Renault Megane  *Bose*',
#  'updateDate': '2019-06-09 8:23:30',
#  'userBlocked': [],
#  'userHideADSStatus': False,
#  'userId': 1301047,
#  'userPhoneData': {'phone': '(099) 382 10 51', 'phoneId': '1053017'},
#  'withInfoBar': False}
