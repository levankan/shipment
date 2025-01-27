from django.db import models

# Create your models here.
# authapp model.
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('main_user', 'Main User'),
        ('logistics', 'Logistics'),
        ('procurement', 'Procurement'),
        ('sales', 'Sales'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='main_user')
