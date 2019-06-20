from django.urls import path, include
from .views import filter_form_render_view, filter_handle, seed_db

urlpatterns = [
    path('', filter_form_render_view, name='filter-render'),
    path('save', filter_handle, name='filter-handle'),
    path('seed-db', seed_db, name='seed-db')
]
