from django.http import JsonResponse
from django.views import View
from main.models import Car
from parsers.utils import CheckUserFilters
from parsers.auto_ria.parser import AutoRiaInnerParse, AutoRiaUpdateParse


class AutoRia(View):

    def get(self, req):
        print('hi')
        # print(Car.objects.count())
        AutoRiaInnerParse()
        # upd_ria.apply_async(countdown=5)
        # r = mul.delay(12, 43)
        # print('hi## hi')
        # AutoRiaInnerParse()

        # car = Car.objects.filter(id=3650).first()
        # celery_serialize_car(car)
        # check_user_filters.apply_async((car.id,), update=True)
        # CheckUserFilters(car.id, update=True)
        # AutoRiaUpdateParse()
        # print(r.get())
        # AutoRiaUpdateParse(3)
        # inner_ria.apply_async(countdown=2)
        return JsonResponse(dict(status='success'))
