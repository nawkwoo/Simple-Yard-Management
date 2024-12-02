# apps/yms_view/forms.py

from django import forms

class MoveEquipmentForm(forms.Form):
    order_id = forms.IntegerField(
        label='주문 ID',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '주문 ID 입력'}),
        required=True
    )
