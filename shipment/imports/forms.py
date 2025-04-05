from django import forms
from .models import Import, Package, Item, PACKAGE_TYPE_CHOICES, INCOTERMS_CHOICES, CURRENCY_CHOICES, FORWARDER_CHOICES

class ImportForm(forms.ModelForm):
    class Meta:
        model = Import
        exclude = ['status']  # ✅ Exclude status field from the form

    # ✅ Ensure dropdown fields render properly
    incoterms = forms.ChoiceField(choices=INCOTERMS_CHOICES, widget=forms.Select())
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES, widget=forms.Select())

    transportation_currency = forms.ChoiceField(choices=CURRENCY_CHOICES, widget=forms.Select(), required=False)
    brokerage_currency = forms.ChoiceField(choices=CURRENCY_CHOICES, widget=forms.Select(), required=False)
    other_currency = forms.ChoiceField(choices=CURRENCY_CHOICES, widget=forms.Select(), required=False)

    commercial_invoice = forms.FileField(required=False, label="Commercial Invoice")
    transportation_invoice = forms.FileField(required=False, label="Transportation Invoice")
    brokerage_invoice = forms.FileField(required=False, label="Brokerage Invoice")
    other_docs = forms.FileField(required=False, label="Other Documents")
    

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['package_type', 'length', 'width', 'height', 'gross_weight']

    package_type = forms.ChoiceField(choices=PACKAGE_TYPE_CHOICES, widget=forms.Select(), required=True)

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_number', 'description_eng', 'description_geo', 'hs_code', 'net_weight']
