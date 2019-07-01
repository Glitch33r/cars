from django.conf import settings
from django.urls import path, include
from .views import filter_form_render_view, filter_handle, seed_db, PaginatorCars
from .views import HomePage
from django.conf.urls.static import static

from django.views.generic import TemplateView

urlpatterns = [
    path('', filter_form_render_view, name='filter-render'),
    path('save', filter_handle, name='filter-handle'),
    path('seed-db', seed_db, name='seed-db'),
    path('home', HomePage.as_view(), name='home'),
    path('cars-list', TemplateView.as_view(template_name='cars_list.html'), name='cars-list'),
    path('cars', PaginatorCars.as_view(), name='cars')
]
