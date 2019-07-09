from datetime import datetime

from django.utils import timezone

from main.models import UserFilter, Profile, Car, Order
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
        attrs = ['model_id', 'mark_id', 'gearbox_id', 'location_id', 'fuel_id', 'body_id', 'dtp', 'cleared']
        valid = True
        print('hi')
        for attr in attrs:
            if getattr(filter, attr) != getattr(self.car, attr):
                valid = False
                if getattr(filter, attr) is None:
                    valid = True
        if getattr(filter, 'blocked') != self.car.user.is_blocked:
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