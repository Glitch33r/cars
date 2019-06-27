from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View


class LoginView(View):
    http_method_names = ['get']

    def get(self):
        pass