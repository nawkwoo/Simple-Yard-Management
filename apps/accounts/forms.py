from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class AdminSignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'gender', 'birth_date', 'has_car']

class StaffSignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'gender', 'birth_date', 'has_car']