
import re
from datetime import datetime
from django.utils import timezone

from main.models import UserFilter, Profile, Car, Order, Mark, Model
from main.utils import tg_send_message


class CheckUserFilters:

    def __init__(self, car_id, update=False):
        self.car = Car.objects.filter(id=car_id).first()
        self.saller = self.car.phone
        self.is_update = update
        print('good')
        self.start()
        print('finish')

    def check_is_match(self, filter):
        attrs = ['model_id', 'gearbox_id', 'location_id', 'fuel_id', 'body_id', 'dtp', 'cleared']
        valid = True
        print('hi')
        for attr in attrs:
            if getattr(filter, attr) != getattr(self.car, attr):
                valid = False
                if getattr(filter, attr) is None:
                    valid = True
        if getattr(filter,  'mark_id') != self.car.model.mark.id:
            valid = False
        if getattr(filter, 'blocked') != self.saller.is_blocked:
            valid = False
        if getattr(filter, 'dealer') == self.saller.is_dealer:
            valid = False
        print(valid, 'after "check_is_match()"')
        if valid:
            return True
        return False

    def add_car_to_filter(self, filter):
        filter.car_ids = filter.car_ids + str(self.car.id) + ', '
        filter.save()

    def start(self):
        if self.is_update:
            for filter in UserFilter.objects.filter(car_ids__contains=str(self.car.id)):
                if filter.is_active():
                    print('send message')
                    tg_send_message(profile=filter.user, car=self.car, update=self.is_update)
        else:
            for filter in UserFilter.get_active():
                if self.check_is_match(filter):
                    tg_send_message(profile=filter.user, car=self.car, update=self.is_update)
                    self.add_car_to_filter(filter)


class CheckIsActiveUsers:

    def __init__(self):
        self.start()

    def start(self):
        for user in Profile.objects.all():
            if user.is_payed:
                user.is_active = True
            else:
                user.is_active = False


def serialize_car(car: object):
    print(vars(car))


class GetModel():

    def __init__(self, mark, model):
        self.mark = mark
        self.model = model

    def get_model_id(self):
        if self.mark and self.model:
            self.mark = re.sub(r"^iz$", "izh", self.mark)
            self.mark = re.sub(r"greatwall", "great-wall", self.mark)
            self.mark = re.sub(r"ssang-yong", "ssangyong", self.mark)
            self.mark = re.sub(r"(moscvich|moskvich-azlk)", "moskvich", self.mark)
            self.mark = re.sub(r"mercedes-benz", "mercedes", self.mark)
            self.mark = re.sub(r"alfaromeo", "alfa-romeo", self.mark)
            self.mark = re.sub(r"landrover", "land-rover", self.mark)

            mark_obj = Mark.objects.filter(eng=self.mark).first()
            mark_id = mark_obj.id if mark_obj else None

            if mark_id:
                self.model = re.sub(r"(\-gruz|\-pass|\-1)$", "", self.model)

                if mark_id == 22:
                    self.model = re.sub(r"seriya", "series", self.model)
                    self.model = re.sub(r"^([0-9])[0-9]{2}$", "\1-series", self.model)
                elif mark_id == 34:
                    self.model = re.sub(r"tigo", "tiggo", self.model)
                    self.model = re.sub(r"sweet-qq", "qq", self.model)
                    self.model = re.sub(r"^qq.+?$", "qq", self.model)
                    self.model = re.sub(r"^kimo.+?$", "kimo", self.model)
                    self.model = re.sub(r"a21", "elara", self.model)
                elif mark_id == 35:
                    self.model = re.sub(r"lacetti(-variant|-hatchback|-furgon|-pick-up|-sedan)", "lacetti", self.model)
                    self.model = re.sub(r"lanos(-sens|-hatchback|-furgon|-pick-up|-sedan|-2)", "lanos", self.model)
                elif mark_id == 36:
                    self.model = re.sub(r"300(c|m|s)", "300-\1", self.model)
                elif mark_id == 40:
                    self.model = re.sub(r"lanos(-sens|-hatchback|-furgon|-pick-up|-sedan|-2)", "lanos", self.model)
                elif mark_id == 59:
                    self.model = re.sub(r"new-500", "500", self.model)
                    self.model = re.sub(r"^500(l|x)$", "500", self.model)
                    self.model = re.sub(r"grandepunto", "grande-punto", self.model)
                elif mark_id == 62:
                    self.model = re.sub(r"fiesta-st", "fiesta", self.model)
                    self.model = re.sub(r"^connect$", "tourneo-connect", self.model)
                    self.model = re.sub(r"^tourneo$", "tourneo-connect", self.model)
                    self.model = re.sub(r"^connect-tourneo$", "tourneo-connect", self.model)
                elif mark_id == 67:
                    self.model = re.sub(r"emgrandx(\d)", "emgrand-x\1", self.model)
                    self.model = re.sub(r"emgrand[0-9\-].+?$", "emgrand", self.model)
                    self.model = re.sub(r"emgrand-?([0-9])$", "emgrand", self.model)
                elif mark_id == 71:
                    self.model = re.sub(r"^.*?voleex.*?$", "voleex", self.model)
                    self.model = re.sub(r"^.*?haval.*?$", "haval", self.model)
                elif mark_id == 78:
                    self.model = re.sub(r"^.*?civic.*?$", "civic", self.model)
                    self.model = re.sub(r"^.*?accord.*?$", "accord", self.model)
                elif mark_id == 85:
                    self.model = re.sub(r"^h$", "h1", self.model)
                    self.model = re.sub(r"h1-starex", "h1", self.model)
                    self.model = re.sub(r"^h([0-9]{3})$", "h-\1", self.model)
                    self.model = re.sub(r"^.*?ix55.*?$", "ix55", self.model)
                    self.model = re.sub(r"santafe", "santa-fe", self.model)
                elif mark_id == 86:
                    self.model = re.sub(r"^(qx|q|m|g)-([0-9]{2})$", "\1\2", self.model)
                elif mark_id == 95:
                    self.model = re.sub(r"grandcherokee", "grand-cherokee", self.model)
                elif mark_id == 102:
                    self.model = re.sub(r"^.*?rio.*?$", "rio", self.model)
                    self.model = re.sub(r"^.*?cerato.*?$", "cerato", self.model)
                    self.model = re.sub(r"^.*?ceed.*?$", "ceed", self.model)
                elif mark_id == 109:
                    self.model = re.sub(r"^rangeroversport$", "range-rover-sport", self.model)
                    self.model = re.sub(r"^rangerover$", "range-rover", self.model)
                    self.model = re.sub(r"^evoque$", "range-rover-evoque", self.model)
                elif mark_id == 112:
                    self.model = re.sub(r"\-seriya", "", self.model)
                    self.model = re.sub(r"^(es|gs|is|ls|lx|nx|rx|sc)-[0-9]{3}$", "\1", self.model)
                elif mark_id == 122:
                    self.model = re.sub(r"xedos6", "xedos-6", self.model)
                    self.model = re.sub(r"xedos9", "xedos-9", self.model)
                    self.model = re.sub(r"e-2000-2200-bus", "e-series", self.model)
                    self.model = re.sub(r"cx-6", "cx-5", self.model)
                    self.model = re.sub(r"cx([0-9])", "cx-\1", self.model)
                    self.model = re.sub(r"^6-3$", "6", self.model)
                    self.model = re.sub(r"^3-5$", "3", self.model)
                elif mark_id == 125:
                    self.model = re.sub(r"seriya", "class", self.model)
                    self.model = re.sub(r"sprinter-\d+$", "sprinter", self.model)
                    self.model = re.sub(r"w(124|123)", "e-class", self.model)
                    self.model = re.sub(r"^(gl|glk|gls|ml|g|sl|slk|cls|clk|clc|cla|a|b|cl|s|r|v)-[0-9]{3}", "\1-class", self.model)
                    self.model = re.sub(r"^(gl|glk|gls|ml|g|sl|slk|cls|clk|clc|cla|a|b|cl|s|r|v)$", "\1-class", self.model)
                    self.model = re.sub(r"^(gl|glk|gls|ml|g|sl|slk|cls|clk|clc|cla|a|b|cl|s|r|v)\-[0-9]{2}\-amg", "\1-class", self.model)
                    self.model = re.sub(r"^(gls|s)-[0-9]{2}", "\1-class", self.model)
                elif mark_id == 131:
                    self.model = re.sub(r"lanser", "lancer", self.model)
                    self.model = re.sub(r"spacestar", "space-star", self.model)
                    self.model = re.sub(r"spacewagon", "space-wagon", self.model)
                    self.model = re.sub(r"^lancer.+?$", "lancer", self.model)
                    self.model = re.sub(r"pajerosport", "pajero-sport", self.model)
                    self.model = re.sub(r"^l([0-9]00)$", "l-\1", self.model)
                elif mark_id == 135:
                    self.model = re.sub(r"almera-classic", "almera", self.model)
                    self.model = re.sub(r"skyline-gt-r", "skyline", self.model)
                    self.model = re.sub(r"nv200", "nv", self.model)
                    self.model = re.sub(r"^maxima.+?$", "maxima", self.model)
                    self.model = re.sub(r"^micra.+?$", "micra", self.model)
                    self.model = re.sub(r"^qashqai.+?$", "qashqai", self.model)
                elif mark_id == 140:
                    self.model = re.sub(r"record", "rekord", self.model)
                    self.model = re.sub(r"(astra|vectra).+?$", "\1", self.model)
                elif mark_id == 146:
                    self.model = re.sub(r"j5", "g-5", self.model)
                elif mark_id == 151:
                    self.model = re.sub(r"^cayenne.+?$", "cayenne", self.model)
                elif mark_id == 157:
                    self.model = re.sub(r"logan-mcv", "logan", self.model)
                    self.model = re.sub(r"-passenger", "", self.model)
                    self.model = re.sub(r"^(kangoo|scenic|clio|symbol).*?$", "\1", self.model)
                elif mark_id == 178:
                    self.model = re.sub(r"^octavia.+?$", "octavia", self.model)
                    self.model = re.sub(r"^fabia.+?$", "fabia", self.model)
                elif mark_id == 187:
                    self.model = re.sub(r"^impreza.+?$", "impreza", self.model)
                elif mark_id == 189:
                    self.model = re.sub(r"grandvitara", "grand-vitara", self.model)
                elif mark_id == 201:
                    self.model = re.sub(r"rav4", "rav-4", self.model)
                    self.model = re.sub(r"^.*?land-cruiser-prado.*?$", "land-cruiser-prado", self.model)
                    self.model = re.sub(r"^landcruiser$", "land-cruiser", self.model)
                    self.model = re.sub(r"hilux-pick-up", "hilux", self.model)
                    self.model = re.sub(r"corolla-fx", "corolla", self.model)
                    self.model = re.sub(r"^prado$", "land-cruiser-prado", self.model)
                    self.model = re.sub(r"^land-cruiser-[0-9]{3}$", "land-cruiser", self.model)
                elif mark_id == 210:
                    self.model = re.sub(r"^t\d+\-transporter$", "transporter", self.model)
                    self.model = re.sub(r"(-sedan|-variant|-hatchback)", "", self.model)
                    self.model = re.sub(r"passat\-b\d+$", "passat", self.model)
                    self.model = re.sub(r"camper", "transporter", self.model)
                    self.model = re.sub(r"^golf.+?$", "golf", self.model)
                    self.model = re.sub(r"^t[0-9]$", "transporter", self.model)
                    self.model = re.sub(r"^cc$", "passat-cc", self.model)
                    self.model = re.sub(r"^lt-2$", "lt", self.model)
                elif mark_id == 211:
                    self.model = re.sub(r"(-kombi|-k)", "", self.model)
                elif mark_id == 228:
                    self.model = re.sub(r"^.*?(kalina|priora).*?$", "\1", self.model)
                    self.model = re.sub(r"^21(0[1-8]|[1-9][0-9]|099|093|09).*?$", "21\1", self.model)
                    self.model = re.sub(r"1111-oka", "oka", self.model)
                elif mark_id == 230:
                    self.model = re.sub(r"^.*?sobol.*?$", "sobol", self.model)
                    self.model = re.sub(r"^.*?pobeda.*?$", "20", self.model)
                    self.model = re.sub(r"^.*?gazel.*?$", "gazel", self.model)
                    self.model = re.sub(r"24-10-volga", "24", self.model)
                    self.model = re.sub(r"12-zim", "12", self.model)
                    self.model = re.sub(r"2790", "gazel", self.model)
                    self.model = re.sub(r"^(21|23|24|24[0-9]{2}|3110[0-9]?|3109)$", "volga", self.model)
                elif mark_id == 236:
                    self.model = re.sub(r"^(1102|1140).*?$", "tavriya", self.model)
                    self.model = re.sub(r"^(1105|1125).*?$", "dana", self.model)
                    self.model = re.sub(r"^1103.*?$", "slavuta", self.model)
                    self.model = re.sub(r"(tavria-pickup|tavria)", "tavriya", self.model)
                    self.model = re.sub(r"lanos(-sens|-hatchback|-furgon|-pick-up|-pickup|-sedan)", "lanos", self.model)
                elif mark_id == 240:
                    self.model = re.sub(r"^(21|27)([0-9]{2}).*?$", "\1\2", self.model)
                elif mark_id == 242 and self.model == '2125':
                    mark_id = 240
                elif mark_id == 242:
                    self.model = re.sub(r"^.*?2141.*?$", "2141", self.model)
                    self.model = re.sub(r"^.*?2135.*?$", "2335", self.model)
                elif mark_id == 254:
                    self.model = re.sub(r"^.*?hunter.*?$", "hunter", self.model)
                    self.model = re.sub(r"^.*?patriot.*?$", "patriot", self.model)

                model_obj = Model.objects.filter(eng=self.model, mark_id=mark_id).first()
                model_id = model_obj.id if model_obj else None

                if model_id:
                    return model_id

        print('Not save {} {}'.format(self.mark, self.model))
        return None
