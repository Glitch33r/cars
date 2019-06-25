from django.views.generic import View
from django.http import HttpResponse

from .parser import Rst

class RstView(View):

    def get(self, request):
        try:
            pages = int(request.GET['pages'])
        except: pages = None

        if pages:
            Rst(pages)
        Rst(1)

        return HttpResponse('DONE')
