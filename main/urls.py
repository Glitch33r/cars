from django.conf import settings
from django.urls import path, include
from .views import filter_form_render_view, filter_handle, seed_db, PaginatorCars, models_view
from .views import HomePage
from django.conf.urls.static import static

urlpatterns = [
    path('', filter_form_render_view, name='filter-render'),
    path('save', filter_handle, name='filter-handle'),
    path('seed-db', seed_db, name='seed-db'),
    path('home', HomePage.as_view(), name='home'),
    path('ajax/models/<int:id>', models_view, name='models'),
    path('cars', PaginatorCars.as_view(), name='cars')
]
