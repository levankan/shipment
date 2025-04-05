import os
from django.db import models
from django_countries.fields import CountryField

# ✅ Function to generate dynamic file path
def upload_to(instance, filename):
    return os.path.join('uploads/imports', instance.unique_number, filename)

PACKAGE_TYPE_CHOICES = [
    ('PALLET', 'Pallet'),
    ('BOX', 'Box'),
    ('KIT', 'Kit'),
]

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

STATUS_CHOICES = [
    ('Active', 'Active'),
    ('Finished', 'Finished'),
    ('Delivered', 'Delivered'), 
]

CURRENCY_CHOICES = [
    ('USD', 'USD - US Dollar'),
    ('EUR', 'EUR - Euro'),
    ('GBP', 'GBP - British Pound'),
    ('GEL', 'GEL - Georgian Lari'),
]

FORWARDER_CHOICES = [
    ('Gebruder Weiss', 'Gebruder Weiss'),
    ('DBschenker', 'DBschenker'),
    ('DSV-Transglobe', 'DSV-Transglobe'),
    ('Gianti Logistics', 'Gianti Logistics'),
    ('FedEx', 'FedEx'),
    ('DHL', 'DHL'),
    ('UPS', 'UPS'),
    ('Other', 'Other'),
]

# ✅ Import Model with File Upload Fields
class Import(models.Model):
    unique_number = models.CharField(max_length=10, unique=True, editable=False)
    vendor_name = models.CharField(max_length=100)
    country = CountryField() 
    incoterms = models.CharField(max_length=3, choices=INCOTERMS_CHOICES)
    operation = models.CharField(max_length=50, choices=[
        ('import', 'Import'),
        ('inward_processing', 'Inward Processing')
    ])
    is_dangerous = models.BooleanField(default=False)
    is_stackable = models.BooleanField(default=True)
    pickup_address = models.TextField()
    currency = models.CharField(max_length=4, choices=CURRENCY_CHOICES, default='USD')
    forwarder_company = models.CharField(max_length=50, choices=FORWARDER_CHOICES, default="Other")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    date_created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)

    # ✅ File Upload Fields
    commercial_invoice = models.FileField(upload_to=upload_to, blank=True, null=True)
    transportation_invoice = models.FileField(upload_to=upload_to, blank=True, null=True)
    brokerage_invoice = models.FileField(upload_to=upload_to, blank=True, null=True)
    other_docs = models.FileField(upload_to=upload_to, blank=True, null=True)

    #transportation and other charges

    transportation_cost = models.FloatField(blank=True, null=True)
    transportation_currency = models.CharField(max_length=4, choices=CURRENCY_CHOICES, blank=True, null=True)

    brokerage_cost = models.FloatField(blank=True, null=True)
    brokerage_currency = models.CharField(max_length=4, choices=CURRENCY_CHOICES, blank=True, null=True)

    other_cost = models.FloatField(blank=True, null=True)
    other_currency = models.CharField(max_length=4, choices=CURRENCY_CHOICES, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.unique_number:
            last_import = Import.objects.order_by('-id').first()
            if last_import and last_import.unique_number.startswith("IMP"):
                try:
                    number = int(last_import.unique_number.replace("IMP", "")) + 1
                except ValueError:
                    number = 1
            else:
                number = 1

            self.unique_number = f"IMP{str(number).zfill(5)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.unique_number



class ImportDetail(models.Model):
    import_instance = models.ForeignKey(Import, related_name="import_details", on_delete=models.CASCADE)
    po_number = models.CharField(max_length=50)
    line_number = models.IntegerField()
    item_number = models.CharField(max_length=50)
    description_eng = models.TextField()
    quantity = models.IntegerField()
    unit_cost = models.FloatField()
    line_cost = models.FloatField(blank=True, null=True)  # ✅ Allow null for auto-calculation

    def save(self, *args, **kwargs):
        # ✅ Automatically calculate line_cost if not provided
        if self.line_cost is None:
            self.line_cost = self.unit_cost * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.import_instance.unique_number} - {self.item_number}"


class Package(models.Model):
    import_instance = models.ForeignKey(Import, related_name="packages", on_delete=models.CASCADE)
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPE_CHOICES)
    length = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    gross_weight = models.FloatField()

    def __str__(self):
        return f"{self.package_type} - {int(self.length)}x{int(self.width)}x{int(self.height)} - {int(self.gross_weight)}kg"


class Item(models.Model):
    item_number = models.CharField(max_length=50, unique=True)  # ✅ Unique Item Number
    description_eng = models.CharField(max_length=255)
    description_geo = models.CharField(max_length=255, blank=True, null=True)
    hs_code = models.CharField(max_length=50, blank=True, null=True)
    net_weight = models.FloatField()

    def __str__(self):
        return f"{self.item_number} - {self.description_eng}"
