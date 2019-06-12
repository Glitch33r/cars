from django.shortcuts import render
from django.views import View




class AutoRia(View):

    def get(self, req):
        AutoRiaInnerParse()
