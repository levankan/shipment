from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),  # Custom login view
    path('logout/', views.logout_view, name='logout'),  # Custom logout view
    path('home/', views.home, name='home'),  # Home page
]
