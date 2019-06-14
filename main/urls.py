from django.urls import path, include
from .views import filter_form_render_view, filter_handle

# from parsers.rst.views import RstView

urlpatterns = [
    path('', filter_form_render_view, name='filter-render'),
    path('save', filter_handle, name='filter-handle')
]
