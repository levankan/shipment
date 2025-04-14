from django.urls import path
from . import views

urlpatterns = [
    path('scan/', views.scan_tracking_view, name='warehouse_scan'),
    path('add-email/', views.add_notification_email, name='add_notification_email'),
    path('manage-emails/', views.manage_notification_emails, name='manage_notification_emails'),
    path('delete-email/<int:email_id>/', views.delete_notification_email, name='delete_notification_email'),
]
