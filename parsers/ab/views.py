from django.views.generic import View
from django.http import HttpResponse

from .parser import Ab

class AbView(View):

    def get(self, request):
        ab = Ab()
        return HttpResponse('DONE')
