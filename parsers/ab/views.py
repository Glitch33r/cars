from threading import Thread
from django.views.generic import View
from django.http import HttpResponse

from main.models import Car
from .parser import Ab


class AbParse(View):

    def get(self, request):
        ab_obj = Ab()
        thread_1 = Thread(target=ab_obj.parse, args=(1, 250))
        thread_2 = Thread(target=ab_obj.parse, args=(251, 500))
        thread_1.start()
        thread_2.start()
        thread_1.join()
        thread_2.join()
        return HttpResponse('DONE')


class AbUpdate(View):

    def get(self, request):
        ab_obj = Ab()
        for car in Car.objects.filter(ab_car_id__isnull=False, sold=False):
            ab_obj.update(car)
        print('>>>>> FINISHED <<<<<')
        return HttpResponse('DONE')
