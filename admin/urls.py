from django.urls import path
from admin.views import AnaliticView, AnaliticMileageView, AnaliticSelltimeView

urlpatterns = [
    path('analitic/', AnaliticView.as_view(), name='analitic'),
    path('analitic/mileage/', AnaliticMileageView.as_view(), name='analitic-mileage'),
    path('analitic/selltime/', AnaliticSelltimeView.as_view(), name='analitic-selltime'),
]
