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
