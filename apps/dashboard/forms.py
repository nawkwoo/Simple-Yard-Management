# apps/dashboard/forms.py

from django import forms

class CSVUploadForm(forms.Form):
    """
    CSV 파일 업로드를 위한 폼.
    """
    file = forms.FileField(
        label="CSV 파일 업로드",
        help_text="운송 주문을 일괄 업로드할 CSV 파일을 선택해주세요."
    )
