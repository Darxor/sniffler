from django import forms


class ScanForm(forms.Form):
    path = forms.CharField(label="Path", max_length=255)
