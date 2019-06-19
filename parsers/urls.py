from django.urls import path, include
from .olx.views import run
from .rst.views import RstView

urlpatterns = [
    path('olx', run, name='parse-olx'),
    path('rst', RstView.as_view(), name='parse-rst'),
]
