# imports/models.
from django.db import models

class Import(models.Model):
    INCOTERMS_CHOICES = [
        ('NoN', 'NoN'),
        ('EXW', 'EXW – Ex Works'),
        ('FCA', 'FCA – Free Carrier'),
        ('CPT', 'CPT – Carriage Paid To'),
        ('CIP', 'CIP – Carriage and Insurance Paid To'),
        ('DAP', 'DAP – Delivered at Place'),
        ('DPU', 'DPU – Delivered at Place Unloaded'),
        ('DDP', 'DDP – Delivered Duty Paid'),
    ]

    PACKAGE_TYPE_CHOICES = [
        ('PALLET', 'Pallet'),
        ('BOX', 'Box'),
        ('KIT', 'Kit'),
    ] 

    unique_number = models.CharField(max_length=10, unique=True, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100)  # Country of origin/destination
    incoterms = models.CharField(max_length=3, choices=INCOTERMS_CHOICES, default='NoN')  # Dropdown menu for Incoterms
    operation = models.CharField(
        max_length=50,
        choices=[
            ('import', 'Import'),
            ('inward_processing', 'Inward Processing')
        ],
    )
    package_type = models.CharField(max_length=10, choices=PACKAGE_TYPE_CHOICES, default='BOX')  # Added package type

    length = models.FloatField()  # Dimensions: Length
    width = models.FloatField()   # Dimensions: Width
    height = models.FloatField()  # Dimensions: Height
    gross_weight = models.FloatField()  # Gross weight in kg
    is_dangerous = models.BooleanField(default=False)  # Is it dangerous?
    is_stackable = models.BooleanField(default=True)  # Is it stackable?
    pickup_address = models.TextField()  # Address for pickup
    date_created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.unique_number:
            # Generate a unique number in the format 'IMP00001'
            last_import = Import.objects.all().order_by('id').last()
            if last_import:
                number = int(last_import.unique_number.replace("IMP", "")) + 1
            else:
                number = 1
            self.unique_number = f"IMP{str(number).zfill(5)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.unique_number
