# apps/yms_view/models.py

from django.db import models
from apps.yms_edit.models import Yard, YardInventory, Truck, Chassis, Container, Trailer, Site
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction

class Transaction(models.Model):
    """트랜잭션 모델"""
    EQUIPMENT_TYPE_CHOICES = [
        ('Truck', 'Truck'),
        ('Chassis', 'Chassis'),
        ('Container', 'Container'),
        ('Trailer', 'Trailer'),
        ('PersonalVehicle', 'Personal Vehicle'),
    ]

    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPE_CHOICES)
    equipment = models.PositiveIntegerField(null=True, blank=True)  # 장비 ID (Truck, Chassis 등)
    departure_yard = models.ForeignKey(Yard, on_delete=models.PROTECT, related_name="transactions_departed")
    arrival_yard = models.ForeignKey(Yard, on_delete=models.PROTECT, related_name="transactions_arrived")
    movement_time = models.DateTimeField(auto_now_add=True)  # 이동 시간
    details = models.TextField(blank=True, null=True)  # 추가적인 정보

    def __str__(self):
        return f"{self.get_equipment_type_display()} 이동: {self.departure_yard} -> {self.arrival_yard} ({self.movement_time})"
