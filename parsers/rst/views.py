from django.shortcuts import render
from django.views.generic import View

from .parser import Rst

class RstView(View):

    def get(self, request):
        Rst(1)
