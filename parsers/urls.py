from django.urls import path, include
from .olx.views import run
from .rst.views import RstView
from .ab.views import AbParse, AbUpdate
from .auto_ria.views import AutoRia
from .besplatka.views import Bsp

urlpatterns = [
    path('olx', run, name='parse-olx'),
    path('rst', RstView.as_view(), name='parse-rst'),
    path('ab', AbParse.as_view(), name='parse-ab'),
    path('ab-upd', AbUpdate.as_view(), name='update-ab'),
    path('besplatka', Bsp.as_view(), name='parse-besplatka'),
    path('autoria', AutoRia.as_view(), name='parse-autoria'),
]
