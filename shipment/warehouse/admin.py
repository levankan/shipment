from django.contrib import admin

# Register your models here.
# warehouse/admin.py

from django.contrib import admin
from .models import NotificationEmail

admin.site.register(NotificationEmail)
