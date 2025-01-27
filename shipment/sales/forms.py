from django import forms

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label="Upload Excel File",
        widget=forms.ClearableFileInput(attrs={'accept': '.xlsx, .xls'}),
    )

    def clean_excel_file(self):
        file = self.cleaned_data.get('excel_file')

        # Check file extension
        if not file.name.endswith(('.xlsx', '.xls')):
            raise forms.ValidationError("Invalid file format. Please upload an Excel file.")
        
        return file