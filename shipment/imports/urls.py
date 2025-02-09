from django.urls import path
from .views import (
    register_import, import_list, import_detail, edit_import, delete_import,
    upload_excel, finish_import, export_import_excel, export_all_imports_excel, export_items_excel, upload_items
)

urlpatterns = [
    path('register/', register_import, name='register_import'),
    path('', import_list, name='import_list'),
    path('export_all_excel/', export_all_imports_excel, name='export_all_imports_excel'),  # ✅ MOVE THIS ABOVE!
    path('upload_items/', upload_items, name='upload_items'),
    path('export_items_excel/', export_items_excel, name='export_items_excel'),
    path('<str:unique_number>/', import_detail, name='import_detail'),  # ❌ Was catching everything before
    path('<str:unique_number>/edit/', edit_import, name='edit_import'),
    path('<str:unique_number>/delete/', delete_import, name='delete_import'),
    path('upload_excel/', upload_excel, name='upload_excel'),
    path('<str:unique_number>/finish/', finish_import, name='finish_import'),
    path('<str:unique_number>/export_excel/', export_import_excel, name='export_import_excel'),
]

