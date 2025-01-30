from django import forms
from .models import Import, Package

class ImportForm(forms.ModelForm):
    class Meta:
        model = Import
        fields = [
            'name',
            'description',
            'country',
            'incoterms',
            'operation',
            'is_dangerous',
            'is_stackable',
            'pickup_address',
        ]

    incoterms = forms.ChoiceField(
        choices=[('', 'Please select an option')] + Import.INCOTERMS_CHOICES,
        widget=forms.Select(),
        error_messages={'required': 'Please select an item from the list.'}
    )

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['package_type', 'length', 'width', 'height', 'gross_weight']
    
    package_type = forms.ChoiceField(
        choices=[('', 'Please select an option')] + Import.PACKAGE_TYPE,
        widget=forms.Select(),
        required=False  # ❗ Make this optional so it's not required on Import submission
    )
