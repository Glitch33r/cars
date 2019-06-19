from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from .parser import AutoRiaInnerParse


class AutoRia(View):

    def get(self, req):
        print('hi')
        AutoRiaInnerParse()
        return JsonResponse(dict(status='success'))