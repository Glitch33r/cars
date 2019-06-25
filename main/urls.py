from django.conf import settings
from django.urls import path, include
from .views import filter_form_render_view, filter_handle, seed_db
from django.conf.urls.static import static

from django.views.generic import TemplateView

urlpatterns = [
    path('', filter_form_render_view, name='filter-render'),
    path('save', filter_handle, name='filter-handle'),
    path('seed-db', seed_db, name='seed-db'),
    path('home', TemplateView.as_view(template_name='home.html'), name='home'),
]
