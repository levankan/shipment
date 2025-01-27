from django.db import models

# Create your models here.
import uuid
import random
from django.db import models
from datetime import datetime

class Sale(models.Model):
    serial_lot = models.CharField(max_length=100)
    document_number = models.CharField(max_length=100)
    item_number = models.CharField(max_length=100)
    item_reference_number = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    unit_of_measure_code = models.CharField(max_length=50, blank=True, null=True)
    box = models.CharField(max_length=100, blank=True, null=True)
    invoice_number = models.CharField(max_length=100)
    invoice_date = models.DateField()
    shipment_number = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    carbon_qty = models.FloatField(blank=True, null=True)
    lot_carbon = models.CharField(max_length=100, blank=True, null=True)
    sales_order_number = models.CharField(max_length=100)
    sales_order_line_number = models.CharField(max_length=100, blank=True, null=True)
    customer_order_number = models.CharField(max_length=100)
    customer_order_line_number = models.CharField(max_length=100, blank=True, null=True)
    sales_amount_actual = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    posting_date = models.DateField(blank=True, null=True)
    project_code = models.CharField(max_length=100, blank=True, null=True)
    hs_code = models.CharField(max_length=100, blank=True, null=True)
    net_weight_kg = models.FloatField(blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    batch_number = models.CharField(max_length=50, unique=True, blank=True)  # Unique batch number
    lu_number = models.CharField(max_length=100, blank=True, null=True)  # New LU Number column

    def save(self, *args, **kwargs):
        # Generate a unique batch number if not already set
        if not self.batch_number:
            self.batch_number = self.generate_unique_batch_number()

        super().save(*args, **kwargs)

    def generate_unique_batch_number(self):
        while True:
            current_year = datetime.now().year
            current_month = datetime.now().month
            random_number = random.randint(1000, 9999)
            batch_number = f"SALE{current_year}{current_month:02}{random_number}"

            # Check if the batch number is unique
            if not Sale.objects.filter(batch_number=batch_number).exists():
                return batch_number

    def __str__(self):
        return f"{self.batch_number} - {self.serial_lot}"