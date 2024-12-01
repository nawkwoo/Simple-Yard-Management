# apps/yms_edit/forms.py

from django import forms
from .models import Division, Yard, Site, Truck, Chassis, Container, Trailer

# --- Yard Form ---
class YardCreateForm(forms.ModelForm):
    """야드 추가/수정 폼"""
    division = forms.ModelChoiceField(
        queryset=Division.objects.all(),
        empty_label="디비전 선택",
        label="디비전"
    )
    equipment_types = forms.MultipleChoiceField(
        choices=Site.EQUIPMENT_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="사이트 종류",
        required=True
    )

    class Meta:
        model = Yard
        fields = ['division', 'yard_id', 'address', 'latitude', 'longitude', 'is_active']  # 'address', 'latitude', 'longitude' 추가
        widgets = {
            'latitude': forms.HiddenInput(),  # 위도 필드를 숨김 처리
            'longitude': forms.HiddenInput(),  # 경도 필드를 숨김 처리
        }

    def __init__(self, *args, **kwargs):
        """기존 데이터 초기값 설정"""
        instance = kwargs.get('instance')
        if instance:
            kwargs['initial'] = kwargs.get('initial', {})
            kwargs['initial']['equipment_types'] = [
                site.equipment_type for site in instance.sites.all()
            ]
        super().__init__(*args, **kwargs)

# --- Truck Form ---
class TruckForm(forms.ModelForm):
    """트럭 추가/수정 폼"""
    class Meta:
        model = Truck
        fields = ['site', 'truck_id', 'serial_number', 'image', 'is_active']
        widgets = {
            'truck_id': forms.TextInput(attrs={'placeholder': '4-digit Truck ID'}),
            'serial_number': forms.TextInput(attrs={'placeholder': 'Enter Serial Number'}),
        }
        help_texts = {
            'site': "트럭을 추가할 사이트를 선택하세요.",
            'truck_id': "예시: 1234 (4자리 숫자)",
            'serial_number': "트럭의 고유 일련번호를 입력하세요.",
            'image': "트럭의 이미지를 업로드하세요.",
            'is_active': "활성화 여부를 선택하세요."
        }


# --- Chassis Form ---
class ChassisForm(forms.ModelForm):
    """샤시 추가/수정 폼"""
    class Meta:
        model = Chassis
        fields = ['site', 'chassis_id', 'type', 'serial_number', 'image', 'is_active']
        widgets = {
            'chassis_id': forms.TextInput(attrs={'placeholder': '4 uppercase letters'}),
        }
        help_texts = {
            'site': "샤시를 추가할 사이트를 선택하세요.",
            'chassis_id': "예시: ABCD (4개의 대문자)",
            'type': "샤시의 유형을 선택하세요.",
            'serial_number': "샤시의 고유 일련번호를 입력하세요.",
            'image': "샤시의 이미지를 업로드하세요.",
            'is_active': "활성화 여부를 선택하세요."
        }


# --- Container Form ---
class ContainerForm(forms.ModelForm):
    """컨테이너 추가/수정 폼"""
    class Meta:
        model = Container
        fields = ['site', 'container_id', 'size', 'type', 'serial_number', 'image', 'is_active']
        widgets = {
            'container_id': forms.TextInput(attrs={'placeholder': 'ABCD1234567'}),
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


# --- Trailer Form ---
class TrailerForm(forms.ModelForm):
    """트레일러 추가/수정 폼"""
    class Meta:
        model = Trailer
        fields = ['site', 'trailer_id', 'size', 'serial_number', 'image', 'is_active']
        widgets = {
            'trailer_id': forms.TextInput(attrs={'placeholder': 'ABCD123456'}),
        }
        help_texts = {
            'site': "트레일러를 추가할 사이트를 선택하세요.",
            'trailer_id': "예시: ABCD123456 (4개의 대문자 + 6개의 숫자)",
            'size': "트레일러의 크기를 선택하세요.",
            'serial_number': "트레일러의 고유 일련번호를 입력하세요.",
            'image': "트레일러의 이미지를 업로드하세요.",
            'is_active': "활성화 여부를 선택하세요."
        }