from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.generic.base import View
from django.core.paginator import Paginator
from main.models import Car, Mark, Gearbox, Location, Model
from main.utils import serialize_cars, filter_cars
from .forms import FilterForm
# Create your views here.
from seed_db.fk_tables import seed_location, seed_body, seed_color, seed_fuel, seed_gearbox, seed_mark, seed_model
from django.views.decorators.http import require_GET


class HomePage(View):
    template_name = 'home.html'

    def get(self, request, **kwargs):
        car_list = Car.objects.all()
        if request.GET.dict():
            car_list = filter_cars(request.GET.dict())
        paginator = Paginator(car_list, 5)
        cars = paginator.get_page(request.GET.get('page'))
        context = dict()
        context['marks'] = Mark.objects.all()
        context['gearboxs'] = Gearbox.objects.all()
        context['locations'] = Location.objects.all()
        context['cars'] = serialize_cars(cars)
        return render(request, 'home.html', context=context)

    def post(self, request, **kwargs):
        # cars =
        data = request.POST
        print(data.keys())
        mark = data.get('model')
        print(data.get('model'), data.get('start_year'))
        return redirect('home')


class PaginatorCars(View):
    http_method_names = ['get']

    def get(self, request):
        car_list = Car.objects.all()
        paginator = Paginator(car_list, 5)
        cars = paginator.get_page(request.GET.get('page'))
        cars = serialize_cars(cars)
        return JsonResponse({'status': 'success', 'cars': cars})


@require_GET
def models_view(request, id):
    models = Model.objects.filter(mark=id)
    response = []
    for model in models:
        model = vars(model)
        [model.pop(key) for key in ['_state', 'mark_id', 'ria_id', 'eng']]
        print(model)
        response.append(model)
    return JsonResponse({'data': response})


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
