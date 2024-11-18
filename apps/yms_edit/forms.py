from django import forms
from .models import Division, Yard, Site, Truck, Chassis, Container, Trailer

class YardCreateForm(forms.ModelForm):
    """야드 추가 폼"""
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
        fields = ['division', 'yard_id', 'is_active']


class TruckForm(forms.ModelForm):
    class Meta:
        model = Truck
        fields = ['site', 'truck_id', 'serial_number', 'image', 'is_active']


class ChassisForm(forms.ModelForm):
    class Meta:
        model = Chassis
        fields = ['site', 'chassis_id', 'type', 'serial_number', 'image', 'is_active']


class ContainerForm(forms.ModelForm):
    class Meta:
        model = Container
        fields = ['site', 'container_id', 'size', 'type', 'serial_number', 'image', 'is_active']


class TrailerForm(forms.ModelForm):
    class Meta:
        model = Trailer
        fields = ['site', 'trailer_id', 'size', 'serial_number', 'image', 'is_active']