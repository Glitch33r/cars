from django.urls import path

from main.views import (
    seed_db,
    PaginatorCars,

    HomePage,
    AllCarView,

)


urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('all-car', AllCarView.as_view(), name='all-car'),

    path('seed-db', seed_db, name='seed-db'),
    # path('cars', PaginatorCars.as_view(), name='cars')
]
