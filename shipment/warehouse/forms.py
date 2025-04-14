from django import forms
from .models import NotificationEmail

class NotificationEmailForm(forms.ModelForm):
    class Meta:
        model = NotificationEmail
        fields = ['email']
