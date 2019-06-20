from django.urls import path, include
from .olx.views import run

urlpatterns = [
    path('olx', run, name='parse-olx'),
    path('besplatka', run, name='parse-besplatka'),
]
