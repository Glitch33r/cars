from django.views.generic import TemplateView
from django.http import JsonResponse

from main.models import Car


class AnaliticView(TemplateView):
    template_name = 'admin/analitic.html'


class AnaliticMileageView(TemplateView):
    template_name = 'admin/mileage.html'

    def post(self, request, *args, **kwargs):
        mark = request.POST.get('model__mark')
        model = request.POST.get('model')
        car_qs = Car.objects.filter(model=model, model__mark=mark)

        years = []
        fuels = []
        for car in car_qs:
            years.append(car.year)
            fuels.append(car.fuel)
        years = set(years)
        fuels = set(fuels)

        print(years, fuels)

        for year in years:
            mileages = 0
            count = 0
            for car in car_qs.filter(year=year):
                if car.mileage != 0:
                    mileages += car.mileage
                    count += 1
            mileage = mileages // count
            print(year, mileage)

        return JsonResponse({'status': 'ok', 'qs': mark, 'model': model, 'count': car_qs.count()})


class AnaliticSelltimeView(TemplateView):
    template_name = 'admin/selltime.html'
