from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from apps.yms_edit.models import Yard

class Transaction(models.Model):
    """트랜잭션 모델"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # 다형성
    object_id = models.PositiveIntegerField()
    equipment = GenericForeignKey('content_type', 'object_id')

    departure_yard = models.ForeignKey(Yard, on_delete=models.PROTECT, related_name="transactions_departed")
    arrival_yard = models.ForeignKey(Yard, on_delete=models.PROTECT, related_name="transactions_arrived")

    movement_time = models.DateTimeField(auto_now_add=True)  # 이동 시간
    details = models.TextField(blank=True, null=True)  # 추가적인 정보

    def __str__(self):
        return f"{self.equipment} 이동: {self.departure_yard} -> {self.arrival_yard} ({self.movement_time})"
