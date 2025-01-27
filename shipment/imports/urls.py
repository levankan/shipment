from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_import, name='register_import'),  # Import registration
    path('', views.import_list, name='import_list'),  # List all imports
    path('<str:unique_number>/', views.import_detail, name='import_detail'),  # Detail page for an import
]
