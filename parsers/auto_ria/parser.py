import json

import requests

from main.models import Model, Car, SellerPhone
from parsers.choises import color, location, fuel, body, gearbox


class WordsFormater:

    def engine_parse(self, word: str):
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


class AutoRiaInnerParse(WordsFormater):
    list_posts_way = 'http://auto.ria.com/blocks_search_ajax/search/?countpage=100&category_id=1&page={}'
    post_way = 'https://auto.ria.com/demo/bu/searchPage/v2/view/auto/{}/?lang_id=2'

    def set_saller(self, phone):
        saller = SellerPhone.objects.filter(phone=self.format_phone(phone)).first()
        if saller:
            return saller
        saller = SellerPhone(phone=self.format_phone(phone))
        saller.save()
        return saller

    def __init__(self):
        first_data = json.loads(requests.get(self.list_posts_way.format(0)).content)
        for ids in first_data['result']['search_result']['ids']:
            data = json.loads(requests.get(self.post_way.format(ids)).content)
            model = Model.objects.filter(
                name__contains=self.formating(data['modelNameEng'])).first()
            car = Car(model=model,
                      gearbox_id=gearbox[self.formating(data['autoData']['gearboxName'])],
                      location_id=location[self.formating(data['stateData']['regionName'])],
                      fuel=fuel[self.fuel_parse(data['autoData']['fuelName'])],
                      engine=self.engine_parse(data['autoData']['fuelName']),
                      color=color[self.formating(data[''])],
                      year=data['autoData']['year'],
                      mileage=data['autoData']['raceInt'],
                      price=data['USD'],
                      phone=self.set_saller(data['userPhoneData']['phone']),
                      body_id=data['autoData']['bodyId'],
                      image=data['photoData']['seoLinkF'],
                      dtp=None,

                      )
        for i in range(1, first_data // 100):
            pass

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
    #  'updateDate': '2019-06-09 18:23:30',
    #  'userBlocked': [],
    #  'userHideADSStatus': False,
    #  'userId': 1301047,
    #  'userPhoneData': {'phone': '(099) 382 10 51', 'phoneId': '1053017'},
    #  'withInfoBar': False}
