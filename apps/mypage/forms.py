from django import forms
from apps.accounts.models import Profile, CustomUser


class ProfileEditForm(forms.ModelForm):
    """
    사용자 프로필 편집을 위한 폼.
    """

    class Meta:
        model = Profile
        fields = ['gender', 'birth_date', 'has_car']  # 'username' 필드 제거
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'has_car': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'gender': '성별을 선택하세요.',
            'birth_date': '생년월일을 선택하세요.',
            'has_car': '차량 소유 여부를 선택하세요.',
        }
        labels = {
            'gender': '성별',
            'birth_date': '생년월일',
            'has_car': '차량 소유 여부',
        }


class CustomUserEditForm(forms.ModelForm):
    """
    사용자 이름 편집을 위한 폼.
    """

    class Meta:
        model = CustomUser
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '사용자 이름'}),
        }
        help_texts = {
            'username': '사용자의 이름을 입력하세요.',
        }
        labels = {
            'username': '사용자 이름',
        }

    def clean_username(self):
        """
        사용자 이름의 유효성을 검사합니다.
        """
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("사용자 이름을 입력해주세요.")
        return username
