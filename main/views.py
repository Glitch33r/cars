from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.base import View
from django.core.paginator import Paginator
from main.models import Car, Mark, Gearbox, Location
from main.utils import serialize_cars
from .forms import FilterForm
# Create your views here.
from seed_db.fk_tables import seed_location, seed_body, seed_color, seed_fuel, seed_gearbox, seed_mark, seed_model
from django.views.decorators.http import require_GET


class HomePage(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['marks'] = Mark.objects.all()
        context['gearboxs'] = Gearbox.objects.all()
        context['locations'] = Location.objects.all()

        return context


class PaginatorCars(View):
    http_method_names = ['get']

    def get(self, request):
        car_list = Car.objects.all()
        paginator = Paginator(car_list, 5)
        cars = paginator.get_page(request.GET.get('page'))
        cars = serialize_cars(cars)
        return JsonResponse({'status': 'success', 'cars': cars})


def filter_form_render_view(request):
    filterForm = FilterForm()
    return render(request, 'filter_form.html', {
        'form': filterForm
    })


def filter_handle(request):
    print(request.GET.dict())
    pass


@require_GET
def seed_db(request):
    seed_fuel()
    seed_gearbox()
    seed_body()
    seed_color()
    seed_location()
    seed_mark()
    seed_model()
    return JsonResponse(dict(status='success'))
