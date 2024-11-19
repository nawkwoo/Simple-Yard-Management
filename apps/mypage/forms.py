from django import forms
from apps.accounts.models import CustomUser

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'gender', 'birth_date', 'has_car']