from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import LoginView, FilterSave, ProfileView, get_models

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('filter', FilterSave.as_view(), name='filter'),
    path('models/<int:mark_id>', get_models, name='models'),
    path('profile', ProfileView.as_view(), name='profile'),

]