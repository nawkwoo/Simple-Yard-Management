# apps/yms_edit/forms.py

from django import forms
from .models import Division, Yard, Site, Truck, Chassis, Container, Trailer


# --- Yard Form ---
class YardCreateForm(forms.ModelForm):
    """
    야드 추가/수정 폼
    """
    division = forms.ModelChoiceField(
        queryset=Division.objects.all(),
        empty_label="디비전 선택",
        label="디비전",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    equipment_types = forms.MultipleChoiceField(
        choices=Site.EQUIPMENT_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="사이트 종류",
        required=True
    )

    class Meta:
        model = Yard
        fields = ['division', 'yard_id', 'address', 'latitude', 'longitude', 'is_active']  # 모든 필드 포함
        widgets = {
            'yard_id': forms.TextInput(attrs={
                'placeholder': '예: YD01',
                'class': 'form-control'
            }),
            'address': forms.TextInput(attrs={
                'placeholder': '야드 주소 입력',
                'class': 'form-control'
            }),
            'latitude': forms.HiddenInput(),  # 위도 필드를 숨김 처리
            'longitude': forms.HiddenInput(),  # 경도 필드를 숨김 처리
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        help_texts = {
            'yard_id': '예시: YD01 (야드 ID는 YD로 시작하고 두 자리 숫자로 구성됩니다.)',
            'address': '야드의 주소를 입력하세요.'
        }

    def __init__(self, *args, **kwargs):
        """기존 데이터 초기값 설정"""
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if instance:
            self.fields['equipment_types'].initial = [
                site.equipment_type for site in instance.sites.all()
            ]


# --- Base Equipment Form ---
class BaseEquipmentForm(forms.ModelForm):
    """
    장비 기본 폼 - site 필드 필터링 기능 포함
    """

    def __init__(self, *args, **kwargs):
        equipment_type = kwargs.pop('equipment_type', None)
        super().__init__(*args, **kwargs)
        if equipment_type:
            self.fields['site'].queryset = Site.objects.filter(
                equipment_type=equipment_type,
                is_active=True
            )
            self.fields['site'].empty_label = "사이트 선택"


# --- Truck Form ---
class TruckForm(BaseEquipmentForm):
    """
    트럭 추가/수정 폼
    """

    class Meta:
        model = Truck
        fields = ['site', 'truck_id', 'serial_number', 'image', 'is_active']
        widgets = {
            'truck_id': forms.TextInput(attrs={
                'placeholder': '예: 1234 (4자리 숫자)',
                'class': 'form-control'
            }),
            'serial_number': forms.TextInput(attrs={
                'placeholder': 'Enter Serial Number',
                'class': 'form-control'
            }),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        help_texts = {
            'site': "트럭을 추가할 사이트를 선택하세요.",
            'truck_id': "예시: 1234 (4자리 숫자)",
            'serial_number': "트럭의 고유 일련번호를 입력하세요.",
            'image': "트럭의 이미지를 업로드하세요.",
            'is_active': "활성화 여부를 선택하세요."
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# --- Chassis Form ---
class ChassisForm(BaseEquipmentForm):
    """
    샤시 추가/수정 폼
    """

    class Meta:
        model = Chassis
        fields = ['site', 'chassis_id', 'type', 'serial_number', 'image', 'is_active']
        widgets = {
            'chassis_id': forms.TextInput(attrs={
                'placeholder': '예: ABCD (4개의 대문자)',
                'class': 'form-control'
            }),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={
                'placeholder': 'Enter Serial Number',
                'class': 'form-control'
            }),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        help_texts = {
            'site': "샤시를 추가할 사이트를 선택하세요.",
            'chassis_id': "예시: ABCD (4개의 대문자)",
            'type': "샤시의 유형을 선택하세요.",
            'serial_number': "샤시의 고유 일련번호를 입력하세요.",
            'image': "샤시의 이미지를 업로드하세요.",
            'is_active': "활성화 여부를 선택하세요."
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# --- Container Form ---
class ContainerForm(BaseEquipmentForm):
    """
    컨테이너 추가/수정 폼
    """

    class Meta:
        model = Container
        fields = ['site', 'container_id', 'size', 'type', 'serial_number', 'image', 'is_active']
        widgets = {
            'container_id': forms.TextInput(attrs={
                'placeholder': '예: ABCD1234567 (4개의 대문자 + 7개의 숫자)',
                'class': 'form-control'
            }),
            'size': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={
                'placeholder': 'Enter Serial Number',
                'class': 'form-control'
            }),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        help_texts = {
            'site': "컨테이너를 추가할 사이트를 선택하세요.",
            'container_id': "예시: ABCD1234567 (4개의 대문자 + 7개의 숫자)",
            'size': "컨테이너의 크기를 선택하세요.",
            'type': "컨테이너의 유형을 선택하세요.",
            'serial_number': "컨테이너의 고유 일련번호를 입력하세요.",
            'image': "컨테이너의 이미지를 업로드하세요.",
            'is_active': "활성화 여부를 선택하세요."
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# --- Trailer Form ---
class TrailerForm(BaseEquipmentForm):
    """
    트레일러 추가/수정 폼
    """

    class Meta:
        model = Trailer
        fields = ['site', 'trailer_id', 'size', 'serial_number', 'image', 'is_active']
        widgets = {
            'trailer_id': forms.TextInput(attrs={
                'placeholder': '예: ABCD123456 (4개의 대문자 + 6개의 숫자)',
                'class': 'form-control'
            }),
            'size': forms.Select(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={
                'placeholder': 'Enter Serial Number',
                'class': 'form-control'
            }),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        help_texts = {
            'site': "트레일러를 추가할 사이트를 선택하세요.",
            'trailer_id': "예시: ABCD123456 (4개의 대문자 + 6개의 숫자)",
            'size': "트레일러의 크기를 선택하세요.",
            'serial_number': "트레일러의 고유 일련번호를 입력하세요.",
            'image': "트레일러의 이미지를 업로드하세요.",
            'is_active': "활성화 여부를 선택하세요."
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
