from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('about/', views.about, name='about'),  # About page
    path('sign-in/', auth_views.LoginView.as_view(template_name='custom_auth/login.html'), name='login'),  # Login page
    path('sign-up/', views.sign_up, name='sign_up'),  # Sign-up page
]
