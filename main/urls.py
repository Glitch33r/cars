from django.urls import path

from main.views import (
    seed_db,
    filter_handle,
    filter_form_render_view,
    PaginatorCars,

    HomePage,
    AllCarView,

)


urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('all-car', AllCarView.as_view(), name='all-car'),

    path('seed-db', seed_db, name='seed-db'),
    # path('', filter_form_render_view, name='filter-render'),
    # path('save', filter_handle, name='filter-handle'),
    # path('cars', PaginatorCars.as_view(), name='cars')
]
