from threading import Thread
from django.views.generic import View
from django.http import HttpResponse
from django.core.paginator import Paginator

from main.models import Car
from .parser import Ab


class AbParse(View):

    def get(self, request):
        ab_obj = Ab()
        thread_1 = Thread(target=ab_obj.parse, args=(1, 100))
        thread_2 = Thread(target=ab_obj.parse, args=(101, 200))
        thread_3 = Thread(target=ab_obj.parse, args=(201, 300))
        thread_4 = Thread(target=ab_obj.parse, args=(301, 400))
        thread_5 = Thread(target=ab_obj.parse, args=(401, 500))
        thread_1.start()
        thread_2.start()
        thread_3.start()
        thread_4.start()
        thread_5.start()
        thread_1.join()
        thread_2.join()
        thread_3.join()
        thread_4.join()
        thread_5.join()
        return HttpResponse('DONE')


class AbUpdate(View):

    def get(self, request):
        ab_obj = Ab()
        paginator = Paginator(Car.objects.filter(ab_car_id__isnull=False, sold=False), 5)
        for page in range(1, paginator.num_pages):
            car_list = paginator.page(page)
            thread_1 = Thread(target=ab_obj.update, args=(car_list[0],))
            thread_2 = Thread(target=ab_obj.update, args=(car_list[1],))
            thread_3 = Thread(target=ab_obj.update, args=(car_list[2],))
            thread_4 = Thread(target=ab_obj.update, args=(car_list[3],))
            thread_5 = Thread(target=ab_obj.update, args=(car_list[4],))
            thread_1.start()
            thread_2.start()
            thread_3.start()
            thread_4.start()
            thread_5.start()
            thread_1.join()
            thread_2.join()
            thread_3.join()
            thread_4.join()
            thread_5.join()
        print('>>>>> FINISHED <<<<<')
        return HttpResponse('DONE')
