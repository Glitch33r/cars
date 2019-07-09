from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from main.models import Car
from parsers.auto_ria.tasks import mul, upd_ria, inner_ria
from .parser import AutoRiaInnerParse, AutoRiaUpdateParse
from django.views.generic.list import ListView



class AutoRia(View):

    def get(self, req):
        print('hi')
        print(Car.objects.count())
        AutoRiaInnerParse()
        # upd_ria.apply_async(countdown=5)
        # r = mul.delay(12, 43)
        # print('hi## hi')
        # AutoRiaInnerParse()
        # AutoRiaUpdateParse()
        # print(r.get())
        # AutoRiaUpdateParse()
        # inner_ria.apply_async(countdown=2)
        return JsonResponse(dict(status='success'))
