from django.urls import path

from main.views import (
    seed_db,
    get_marks,
    get_models,
    # PaginatorCars,

    HomePage,
    AllCarView,
    SellerView,
)


urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('all-car/', AllCarView.as_view(), name='all-car'),
    path('seller/<int:pk>/', SellerView.as_view(), name='seller'),

    path('api/marks/', get_marks, name='api-marks'),
    path('api/models/<int:mark_id>', get_models, name='api-models'),

    path('seed-db/', seed_db, name='seed-db'),
    # path('cars', PaginatorCars.as_view(), name='cars')
]
