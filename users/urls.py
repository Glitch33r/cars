from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import LoginView, FilterSave, ProfileView

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('filter', FilterSave.as_view(), name='filter'),
    path('profile', ProfileView.as_view(), name='profile'),

]