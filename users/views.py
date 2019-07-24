from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from django.views.generic.base import View, TemplateView
from django.contrib.auth import forms, authenticate, login

from main.models import Order, Mark, Profile, Gearbox, Location, Model, Car, UserFilter
from main.views import get_filtered_car_qs, filter_qs


class LoginView(View):
    http_method_names = ['get', 'post']

    def get(self, request):
        form = forms.AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})

    def post(self, request, **kwargs):
        data = request.POST.dict()
        # куча проверки проплочен ли аккаунт
        user = authenticate(username=data['username'], password=data['password'])
        if user is not None:
            order = Order.objects.filter(user=user).first()
            if timezone.now() < order.date_expired:
                login(request, user)
                return redirect('home')
            else:
                login(request, user)
                return redirect('home')
        else:
            return redirect('login')


class ProfileView(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super(ProfileView, self).dispatch(request, *args, **kwargs)
        return redirect('login')

    def get(self, request):
        context = dict()
        context['profile'] = Profile.objects.filter(user=request.user).first()
        if context['profile'].is_payed:
            context['date_expired'] = max(Order.objects.filter(user=request.user, date_start__lte=timezone.now()),
                                          key=lambda item: item.date_expired).date_expired
        return render(request, 'profile_page.html', context)


def cleared_filter_qs(data):
    accept_key = ['model', 'mark', 'gearbox', 'location', 'fuel', 'body']
    bool_keys = ['dtp', 'cleared', 'blocked', 'dealer']
    filter_dict = {}
    for key, value in data.items():
        if key in accept_key:
            if value:
                filter_dict[key + '_id'] = value
        elif key in bool_keys:
            filter_dict[key] = bool(value)
    filter_dict['year_start'] = data['year__gte']
    filter_dict['year_finish'] = data['year__lte']
    return filter_dict

class FilterSave(View):
    # template_name = 'filter_page.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super(FilterSave, self).dispatch(request, *args, **kwargs)
        return redirect('login')

    def get(self, request, *args, **kwargs):
        context = dict()
        context['url_post'] = f'http{"s" if request.is_secure() else ""}://{request.META["HTTP_HOST"]}/api/models'
        context['marks'] = Mark.objects.all()
        context['gearboxs'] = Gearbox.objects.all()
        context['locations'] = Location.objects.all()
        return render(request, 'filter_page.html', context)

    def post(self, request, *args, **kwargs):
        data = request.POST.dict()
        data.pop('csrfmiddlewaretoken')
        print(data)
        car_ids = ' '.join([str(car.id) for car in get_filtered_car_qs(data, Car.objects)])
        print('hi')
        print(car_ids)
        print('hi')
        filter_dict = cleared_filter_qs(data)
        print(filter_dict)
        filter_obj = UserFilter(user=Profile.objects.get(user=request.user), car_ids=car_ids, **filter_dict)
        filter_obj.save()
        return redirect('filter')


def get_models(request, mark_id):
    models = [{'id': model.id, 'name': model.name} for model in Model.objects.filter(mark__id=mark_id)]
    return JsonResponse({'models': models})
