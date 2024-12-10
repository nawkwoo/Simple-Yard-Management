# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser
from .models import Profile, Driver

class BaseSignUpForm(UserCreationForm):
    """
    기본 회원가입 폼으로, 공통 필드를 정의합니다.
    """
    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True, label='성별')
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='생년월일'
    )
    has_car = forms.BooleanField(required=False, label='개인 차량 보유 여부')

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'gender', 'birth_date', 'has_car']

    def save(self, commit=True):
        """
        사용자와 연결된 Profile 데이터를 저장합니다.
        """
        user = super().save(commit=False)  # User 객체 생성 (DB에 저장하지 않음)

        if commit:  # commit=True이면 DB에 저장
            user.save()
        
        # Profile 객체 업데이트 또는 생성
        profile, created = Profile.objects.update_or_create(
            user=user,  # user를 기준으로 찾음
            defaults={  # 업데이트할 필드들
                'gender': self.cleaned_data['gender'],
                'birth_date': self.cleaned_data['birth_date'],
                'has_car': self.cleaned_data['has_car'],
            }
        )

        # Profile 객체 업데이트 또는 생성
        profile, created = Driver.objects.update_or_create(
            profile=profile,  # user를 기준으로 찾음
        )        
        return user


class AdminSignUpForm(BaseSignUpForm):
    """
    관리자 회원가입 폼으로, user_type을 'admin'으로 설정합니다.
    """
    user_type = forms.CharField(initial='admin', widget=forms.HiddenInput())

    class Meta(BaseSignUpForm.Meta):
        fields = BaseSignUpForm.Meta.fields + ['user_type']


class StaffSignUpForm(BaseSignUpForm):
    """
    직원 회원가입 폼으로, user_type을 'staff'으로 설정합니다.
    """
    user_type = forms.CharField(initial='staff', widget=forms.HiddenInput())

    class Meta(BaseSignUpForm.Meta):
        fields = BaseSignUpForm.Meta.fields + ['user_type']
