from django import forms
from .models import Import, Package, PACKAGE_TYPE_CHOICES, INCOTERMS_CHOICES, CURRENCY_CHOICES  # ✅ Import CURRENCY_CHOICES

class ImportForm(forms.ModelForm):
    class Meta:
        model = Import
        fields = [
            'vendor_name', 'country', 'incoterms', 'operation',
            'is_dangerous', 'is_stackable', 'pickup_address', 'currency' 
        ]

    # ✅ Now this will work correctly
    incoterms = forms.ChoiceField(choices=INCOTERMS_CHOICES, widget=forms.Select())
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES, widget=forms.Select())  # ✅ Dropdown for currency

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['package_type', 'length', 'width', 'height', 'gross_weight']

    package_type = forms.ChoiceField(choices=PACKAGE_TYPE_CHOICES, widget=forms.Select(), required=True)
