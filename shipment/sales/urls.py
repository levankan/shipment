from django.urls import path
from . import views

urlpatterns = [
    path('', views.sales_home, name='sales_home'),  # Main sales page
    path('shelf/', views.shelf, name='shelf'),
    path('delete-database/', views.delete_sales_database, name='delete_sales_database'),
    path('delete/<int:pk>/', views.delete_line, name='delete_line'),
    path('delete-by-file/', views.delete_by_file, name='delete_by_file'),
]