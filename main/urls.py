from django.urls import path

from main.views import (
    seed_db,
    get_marks,
    get_models,
    # PaginatorCars,

    HomePage,
    AllCarView,
    SellerView,
    Billing,
)


urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('all-car/', AllCarView.as_view(), name='all-car'),
    path('seller/<int:pk>/', SellerView.as_view(), name='seller'),
    path('billing/<int:plan_id>', Billing.as_view(), name='billing'),

    path('api/marks', get_marks, name='get-marks'),
    path('api/models/<int:mark_id>', get_models, name='api-models'),

    path('seed-db/', seed_db, name='seed-db'),
]
