# apps/yms_view/models.py

from django.db import models
from django.core.exceptions import ValidationError
from apps.dashboard.models import Order
from apps.yms_edit.models import Yard, Truck, Chassis, Container, Trailer


class Transaction(models.Model):
    """
    트랜잭션 모델로, 장비의 이동 기록을 관리합니다.
    """
    EQUIPMENT_TYPE_CHOICES = [
        ('Truck', 'Truck'),
        ('Chassis', 'Chassis'),
        ('Container', 'Container'),
        ('Trailer', 'Trailer'),
        ('PersonalVehicle', 'Personal Vehicle'),
    ]

    equipment_type = models.CharField(
        max_length=20,
        choices=EQUIPMENT_TYPE_CHOICES,
        help_text="장비 유형"
    )

    truck = models.ForeignKey(
        Truck,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        help_text="트럭"
    )
    chassis = models.ForeignKey(
        Chassis,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        help_text="샤시"
    )
    container = models.ForeignKey(
        Container,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        help_text="컨테이너"
    )
    trailer = models.ForeignKey(
        Trailer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        help_text="트레일러"
    )
    departure_yard = models.ForeignKey(
        Yard,
        on_delete=models.PROTECT,
        related_name="transactions_departed",
        help_text="출발 야드"
    )
    arrival_yard = models.ForeignKey(
        Yard,
        on_delete=models.PROTECT,
        related_name="transactions_arrived",
        help_text="도착 야드"
    )
    #order_id = models.IntegerField(default=0)  # 기본값 설정
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="transactions_order",
        help_text="주문 ID"
    )
    movement_time = models.DateTimeField(
        auto_now_add=True,
        help_text="이동 시간"
    )
    details = models.TextField(
        blank=True,
        null=True,
        help_text="추가적인 정보"
    )

    def __str__(self):
        equipment = self.get_equipment_display()
        return f"{self.get_equipment_type_display()} 이동: {self.departure_yard} -> {self.arrival_yard} ({self.movement_time})"

    def clean(self):
        """
        트랜잭션 유효성 검사를 수행합니다.
        """
        # 장비 유형에 따라 해당 ForeignKey 필드가 설정되어 있는지 확인
        equipment_fields = {
            'Truck': self.truck,
            'Chassis': self.chassis,
            'Container': self.container,
            'Trailer': self.trailer,
            'PersonalVehicle': None,  # 개인 차량은 ForeignKey가 필요 없음
        }

        selected_equipment = equipment_fields.get(self.equipment_type)

        if self.equipment_type != 'PersonalVehicle':
            if not selected_equipment:
                raise ValidationError(f"{self.equipment_type} 유형의 장비를 선택해야 합니다.")
            # 선택된 장비가 활성화 상태인지 확인
            if not selected_equipment.is_active:
                raise ValidationError(f"선택된 {self.equipment_type}이(가) 비활성화 상태입니다.")
        else:
            if any([self.truck, self.chassis, self.container, self.trailer]):
                raise ValidationError("Personal Vehicle은 별도의 장비 필드를 가질 수 없습니다.")

class EquipmentSpace(models.Model):
    """
    Vieew Yard에 저장되는 Equipment Space 모델
    """
    yard = models.ForeignKey(
        Yard,
        on_delete=models.CASCADE,
        related_name="EquipmentSpace",
        help_text="장비가 속한 야드"
    )

    equipment_type = models.CharField(max_length=10, help_text="장비의 유형 (Truck, Chassis, etc.)")
    equipment_id = models.CharField(
        max_length=15,
        unique=True,
        help_text="장비의 고유 ID"
    )
 
    position = models.IntegerField(
        blank=True,
        null=False,
        help_text="추가적인 정보"
    )