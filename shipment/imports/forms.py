from django import forms
from .models import Import, Package, PACKAGE_TYPE_CHOICES, INCOTERMS_CHOICES  # ✅ Import `INCOTERMS_CHOICES`

class ImportForm(forms.ModelForm):
    class Meta:
        model = Import
        fields = [
            'vendor_name', 'description', 'country', 'incoterms', 'operation',
            'is_dangerous', 'is_stackable', 'pickup_address'
        ]

    # ✅ Now this will work
    incoterms = forms.ChoiceField(choices=INCOTERMS_CHOICES, widget=forms.Select())

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['package_type', 'length', 'width', 'height', 'gross_weight']

    package_type = forms.ChoiceField(choices=PACKAGE_TYPE_CHOICES, widget=forms.Select(), required=True)
