from django.urls import path, include
from .olx.views import run
from .auto_ria.views import AutoRia
from .besplatka.views import Bsp

urlpatterns = [
    path('olx', run, name='parse-olx'),
    path('besplatka', Bsp.as_view(), name='parse-besplatka'),
    path('autoria', AutoRia.as_view(), name='parse-autoria'),
]
