from django.shortcuts import render, redirect
from django.utils import timezone

from django.views.generic.base import View
from django.contrib.auth import forms, authenticate, login

from main.models import Order


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
                pass
        else:
            return redirect('login')
