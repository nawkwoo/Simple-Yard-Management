from django import forms

class CSVUploadForm(forms.Form):
    file = forms.FileField(label="CSV 파일 업로드")