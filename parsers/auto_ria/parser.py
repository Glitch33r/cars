import datetime
import json

import requests

from main.models import Model, Car, SellerPhone
from parsers.choises import location, fuel, gearbox


class WordsFormater:

    def engine_parse(self, word: str):
        # print(f'word:"{word}"')
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
        # print(word)
        exept = 'После ДТП'
        if exept in word:
            return True
        return False

    def format_date(self, word: str):
        if len(word) <= 10:
            return None
        return datetime.datetime.strptime(word, '%Y-%m-%d %H:%M:%S')


class AutoRiaInnerParse(WordsFormater):
    list_posts_way = 'http://auto.ria.com/blocks_search_ajax/search/?countpage={}&category_id=1&page={}&saledParam=2'
    post_way = 'https://auto.ria.com/demo/bu/searchPage/v2/view/auto/{}/?lang_id=2'

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

    def set_car(self, data: dict):
        car = Car(model=self.find_model(data),
                          gearbox_id=gearbox.get(self.formating(data['autoData']['gearboxName'])),
                          location_id=location.get(self.formating(data['stateData']['regionName'])),
                          fuel_id=fuel.get(self.fuel_parse(data['autoData']['fuelName'])),
                          engine=self.engine_parse(data['autoData']['fuelName']),
                          color=None,
                          year=data['autoData']['year'],
                          mileage=data['autoData']['raceInt'],
                          price=data['USD'],
                          phone=self.set_saller(data['userPhoneData']['phone']),
                          body_id=data['autoData'].get('bodyId'),
                          image=data['photoData']['seoLinkF'],
                          dtp=self.check_dtp(data['infoBarText']),
                          sold=data['autoData']['isSold'],
                          cleared=not bool(data['autoData']['custom']),
                          ria_link='https://auto.ria.com' + data['linkToView'],
                          createdAt=self.format_date(data['addDate']),
                          updatedAt=datetime.datetime.now(),
                          last_site_updatedAt=self.format_date(data['updateDate'])
                          )
        return car

    def __init__(self):
        print('Hi, I\'m started')
        first_data = json.loads(requests.get(self.list_posts_way.format(10, 0)).content)

        for i in range(800, first_data['result']['search_result']['count'] // 100):
            print('####', i)
            if i > 900:
                return
            start_data = json.loads(requests.get(self.list_posts_way.format(100, i)).content)
            for ids in start_data['result']['search_result']['ids']:
                data = json.loads(requests.get(self.post_way.format(ids)).content)
                car = self.set_car(data)
                if car.model:
                    car.save()
                else:
                    print(f'car not save Mark:{data["markNameEng"]}, model:{data["modelNameEng"]}, link: https://auto.ria.com{data["linkToView"]}')
                    pass


class AutoRiaUpdateParse(AutoRiaInnerParse):
    list_posts_way = 'http://auto.ria.com/blocks_search_ajax/search/?countpage={}&category_id=1&page={}'
    post_way = 'https://auto.ria.com/demo/bu/searchPage/v2/view/auto/{}/?lang_id=2'

    def __init__(self):
        count = 0
        first_data = json.loads(requests.get(self.list_posts_way.format(10, 0)).content)
        for i in range(0, first_data['result']['search_result']['count'] // 100):
            print('####', i)
            start_data = json.loads(requests.get(self.list_posts_way.format(100, i)).content)
            for ids in start_data['result']['search_result']['ids']:
                if count > 900:
                    return
                count += 1
                print(count)
                data = json.loads(requests.get(self.post_way.format(ids)).content)
                updated = datetime.datetime.strptime(data['updateDate'], '%Y-%m-%d %H:%M:%S')
                start = datetime.datetime.now() - datetime.timedelta(hours=1)
                print(start, updated, datetime.datetime.now())
                updated = updated.timestamp()
                if updated > start.timestamp() and updated < datetime.datetime.now().timestamp():
                    print('good')
                    car = Car.objects.filter(ria_link='https://auto.ria.com' + data['linkToView']).first()
                    if data['autoData']['isSold']:
                        r = (car.delete(), None,)[bool(car)]
                    else:
                        model = self.find_model(data)
                        if model:
                            if car:
                                print(f'updates price {data["USD"]}')
                                car.price = data['USD']
                                car.save()
                            else:
                                car = self.set_car(data)
                                car.save()
                else:
                    pass
                    # print('bad')

# pass


# for i in range(1, first_data['result']['search_result']['count'] // 100):
#     print('####', i)
#     start_data = json.loads(requests.get(self.list_posts_way.format(i)).content)
#     for ids in start_data['result']['search_result']['ids']:
#         data = json.loads(requests.get(self.post_way.format(ids)).content)
#         car = Car(model=self.find_model(data),
#                   gearbox_id=gearbox.get(self.formating(data['autoData']['gearboxName'])),
#                   location_id=location.get(self.formating(data['stateData']['regionName'])),
#                   fuel_id=fuel.get(self.fuel_parse(data['autoData']['fuelName'])),
#                   engine=self.engine_parse(data['autoData']['fuelName']),
#                   color=None,
#                   year=data['autoData']['year'],
#                   mileage=data['autoData']['raceInt'],
#                   price=data['USD'],
#                   phone=self.set_saller(data['userPhoneData']['phone']),
#                   body_id=data['autoData'].get('bodyId'),
#                   image=data['photoData']['seoLinkF'],
#                   dtp=self.check_dtp(data['infoBarText']),
#                   sold=data['autoData']['isSold'],
#                   cleared=not bool(data['autoData']['custom']),
#                   ria_link='https://auto.ria.com' + data['linkToView'],
#                   createdAt=self.format_date(data['addDate']),
#                   updatedAt=datetime.datetime.now(),
#                   last_site_updatedAt=self.format_date(data['updateDate'])
#                   )
#         # if car.model is None and data['modelNameEng'] not in unknown_model:
#         #     unknown_model.append(
#         #         {'name': data['modelNameEng'], 'mark': data['markNameEng'], 'id': data['autoData']['autoId']})
#         #     print(data['modelNameEng'])
#         if car.model:
#             car.save()
#         else:
#             pass
# print('car not saved', car)


# unknown_model = []
# for ids in first_data['result']['search_result']['ids']:
#     data = json.loads(requests.get(self.post_way.format(ids)).content)
#     car = Car(model=self.find_model(data),
#               gearbox_id=gearbox.get(self.formating(data['autoData']['gearboxName'])),
#               location_id=location.get(self.formating(data['stateData']['regionName'])),
#               fuel_id=fuel.get(self.fuel_parse(data['autoData']['fuelName'])),
#               engine=self.engine_parse(data['autoData']['fuelName']),
#               color=None,
#               year=data['autoData']['year'],
#               mileage=data['autoData']['raceInt'],
#               price=data['USD'],
#               phone=self.set_saller(data['userPhoneData']['phone']),
#               body_id=data['autoData'].get('bodyId'),
#               image=data['photoData']['seoLinkF'],
#               dtp=self.check_dtp(data['infoBarText']),
#               sold=data['autoData']['isSold'],
#               cleared=self.check_cleared(data['infoBarText']),
#               ria_link='https://auto.ria.com' + data['linkToView'],
#               createdAt=self.format_date(data['addDate']),
#               updatedAt=datetime.datetime.now(),
#               last_site_updatedAt=self.format_date(data['updateDate'])
#               )
#     # if car.model is None and data['modelNameEng'] not in unknown_model:
#     #     unknown_model.append(
#     #         {'name': data['modelNameEng'], 'mark': data['markNameEng'], 'id': data['autoData']['autoId']})
#     #     print(data['modelNameEng'])
#     if car.model:
#         car.save()
#     else:
#         pass
# print('car not saved', car)

# unknown_model = unknown_model)
# print(unknown_model)

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
