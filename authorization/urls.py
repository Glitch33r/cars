from django.urls import path
from django.contrib.auth import views


urlpatterns = [
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('login', views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('password_reset', views.PasswordResetConfirmView.as_view(), name='password_reset')
]