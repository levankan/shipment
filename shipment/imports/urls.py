from django.urls import path
from .views import register_import, import_list, import_detail, edit_import, delete_import, upload_excel, finish_import

urlpatterns = [
    path('register/', register_import, name='register_import'),
    path('', import_list, name='import_list'),
    path('<str:unique_number>/', import_detail, name='import_detail'),
    path('<str:unique_number>/edit/', edit_import, name='edit_import'),
    path('<str:unique_number>/delete/', delete_import, name='delete_import'),
    path('upload_excel/', upload_excel, name='upload_excel'),
    path('<str:unique_number>/finish/', finish_import, name='finish_import'),  # ✅ Add Finish Route
]
