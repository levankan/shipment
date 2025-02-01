from django.db import models

# ✅ Define Choices Outside the Model (Prevents Import Errors)
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


class Import(models.Model):

    STATUS_CHOICES = [
    ('Active', 'Active'),
    ('Finished', 'Finished'),
    ]


    unique_number = models.CharField(max_length=10, unique=True, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100)
    incoterms = models.CharField(max_length=3, choices=INCOTERMS_CHOICES)
    operation = models.CharField(max_length=50, choices=[
        ('import', 'Import'),
        ('inward_processing', 'Inward Processing')
    ])
    is_dangerous = models.BooleanField(default=False)
    is_stackable = models.BooleanField(default=True)
    pickup_address = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    date_created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.unique_number:
            last_import = Import.objects.all().order_by('id').last()
            number = int(last_import.unique_number.replace("IMP", "")) + 1 if last_import else 1
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
    line_cost = models.FloatField()

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
