from django.http import JsonResponse
from django.views import View
from main.models import Car
from main.utils import upd_ab_utils
from parsers.utils import CheckUserFilters
from parsers.auto_ria.parser import AutoRiaInnerParse, AutoRiaUpdateParse
from main.tasks import check_user_filters
from parsers.tasks import check_is_active_users


class AutoRia(View):

    def get(self, req):
        # print(Car.objects.count())
        for car in Car.objects.exclude(ria_link='').exclude(ab_link=''):
            print(car.id, car.model.mark.name, car.model.name, car.year)
        # AutoRiaInnerParse()
        # upd_ab_utils()
        # check_is_active_users.apply_async(queue='normal')
        # car = Car.objects.filter(id=37173).first()
        # check_user_filters.delay(car.id, update=True)
        print('done')
        return JsonResponse(dict(status='success'))
