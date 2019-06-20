from django.urls import path, include
from .olx.views import run
from .rst.views import RstView
from .ab.views import AbView
from .auto_ria.views import AutoRia

urlpatterns = [
    path('olx', run, name='parse-olx'),
    path('rst', RstView.as_view(), name='parse-rst'),
    path('ab', AbView.as_view(), name='parse-ab'),
    path('besplatka', run, name='parse-besplatka'),
    path('autoria', AutoRia.as_view(), name='parse-autoria'),
]
