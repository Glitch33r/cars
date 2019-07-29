from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from main.models import Car, Fuel


class AnaliticView(TemplateView):
    template_name = 'admin/analitic.html'


class AnaliticMileageView(TemplateView):
    template_name = 'admin/mileage.html'

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        model = request.POST.get('model')
        car_qs = Car.objects.filter(model_id=model)

        fuel_qs = Fuel.objects.all()
        years = set(car.year for car in car_qs)

        fuels = dict()
        for fuel in fuel_qs:
            fuel_data = []
            for year in years:
                mileages = 0
                count = 0
                for car in car_qs.filter(year=year, fuel=fuel):
                    if car.mileage != 0 and car.mileage < 100000:
                        mileages += car.mileage
                        count += 1
                mileage = mileages // count * 1000 if mileages != 0 and count != 0 else 0
                fuel_data.append(mileage)
            if fuel_data and max(fuel_data) > 0:
                fuels[fuel.name.title()] = fuel_data

        response_data = {
            'years': list(years),
            'fuels': fuels
        }
        return JsonResponse(response_data)


class AnaliticSelltimeView(TemplateView):
    template_name = 'admin/selltime.html'
