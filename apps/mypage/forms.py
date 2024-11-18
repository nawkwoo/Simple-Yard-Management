from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'gender', 'birth_date', 'has_car']