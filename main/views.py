from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.views.generic.base import View
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from main.utils import serialize_cars
from main.models import (
    Car,
    SellerPhone,

)
from seed_db.fk_tables import seed_location, seed_body, seed_color, seed_fuel, seed_gearbox, seed_mark, seed_model


def get_pagination_data(request, car_qs, page, item_on_page=10):
    current_path = request.get_full_path()
    paginator = Paginator(car_qs, item_on_page)
    try:
        car_list = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        car_list = paginator.page(page)
    except EmptyPage:
        car_list = paginator.page(paginator.num_pages)

    page = int(page)
    next_page = page + 1
    if next_page > paginator.num_pages:
        next_page = False

    prev_url = current_path.replace('page={}'.format(page), 'page={}'.format(page-1)) \
        if 'page=' in current_path and page != 1 else None
    next_url = current_path.replace('page={}'.format(page), 'page={}'.format(next_page)) \
        if 'page=' in current_path else current_path + '&page={}'.format(next_page) \
        if '?' in current_path else '?page={}'.format(next_page)

    return car_list, page, prev_url, next_url


def filter_qs(params):
    filter_data = dict()
    for key, value in params.items():
        if value != '':
            if key == 'page':
                pass
            elif key == 'cleared':
                filter_data[key] = bool(value != '0')
            elif key == 'dtp':
                filter_data[key] = bool(value != '0')
            else:
                filter_data[key] = value
    return filter_data


def get_filtered_car_qs(params, qs):

    filter_data = filter_qs(params)
    # filter_data = dict()
    # for key, value in params.items():
    #     if value != '':
    #         if key == 'page':
    #             pass
    #         elif key == 'cleared':
    #             filter_data[key] = bool(value != '0')
    #         elif key == 'dtp':
    #             filter_data[key] = bool(value != '0')
    #         else:
    #             filter_data[key] = value

    try:
        car_qs = qs.filter(**filter_data)
    except:
        car_qs = []
    return car_qs


class HomePage(ListView):
    template_name = 'home.html'
    context_object_name = 'car_list'

    def get_queryset(self):
        return Car.objects.filter(sold=False).order_by('-createdAt')[:5]


class AllCarView(ListView):
    template_name = 'all_car.html'

    def get(self, request, *args, **kwargs):
        params = request.GET
        page = params.get('page')

        car_qs = get_filtered_car_qs(params, Car.objects)

        car_list, page, prev_url, next_url = get_pagination_data(request, car_qs, page)

        context = {
            'car_list': car_list,
            'page': page,
            'prev_url': prev_url,
            'next_url': next_url
        }
        return render(request, self.template_name, context)


class SellerView(DetailView):
    template_name = 'seller.html'
    model = SellerPhone
    context_object_name = 'seller'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller = context['seller']
        params = self.request.GET
        page = params.get('page')

        car_qs = get_filtered_car_qs(params, seller.car_set)

        car_list, page, prev_url, next_url = get_pagination_data(self.request, car_qs, page)

        context['car_list'] = car_list
        context['page'] = page
        context['prev_url'] = prev_url
        context['next_url'] = next_url
        context['seller_page'] = True
        return context


class PaginatorCars(View):
    http_method_names = ['get']

    def get(self, request):
        car_list = Car.objects.all()
        paginator = Paginator(car_list, 5)
        cars = paginator.get_page(request.GET.get('page'))
        cars = serialize_cars(cars)
        return JsonResponse({'status': 'success', 'cars': cars})


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
