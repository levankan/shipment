from django import forms
from .models import Import

class ImportForm(forms.ModelForm):
    class Meta:
        model = Import
        fields = [
            'name',
            'description',
            'country',
            'incoterms',
            'operation',
            'package_type', 
            'length',
            'width',
            'height',
            'gross_weight',
            'is_dangerous',
            'is_stackable',
            'pickup_address',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'pickup_address': forms.Textarea(attrs={'rows': 3}),
        }

    # Ensure incoterms and package type fields are dropdowns
    incoterms = forms.ChoiceField(choices=Import.INCOTERMS_CHOICES, widget=forms.Select())
    package_type = forms.ChoiceField(choices=Import.PACKAGE_TYPE_CHOICES, widget=forms.Select())
