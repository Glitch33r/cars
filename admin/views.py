from django.views.generic import TemplateView
from django.http import JsonResponse


class AnaliticView(TemplateView):
    template_name = 'admin/analitic.html'


class AnaliticMileageView(TemplateView):
    template_name = 'admin/mileage.html'

    def post(self, request, *args, **kwargs):
        return JsonResponse({'status': 'ok'})


class AnaliticSelltimeView(TemplateView):
    template_name = 'admin/selltime.html'
