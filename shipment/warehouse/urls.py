from django.urls import path
from .views import scan_tracking_view

urlpatterns = [
    path('scan/', scan_tracking_view, name='warehouse_scan'),
]
