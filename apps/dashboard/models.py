# apps/dashboard/models.py

from django.db import models
from django.conf import settings
from apps.yms_edit.models import Yard, Truck, Chassis, Container, Trailer


class Order(models.Model):
    """
    주문 모델로, 운송 주문의 상세 정보를 저장합니다.
    """
    STATUS_PENDING = 'PENDING'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_FAILED = 'FAILED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]
    # Row 2: Cannot assign "<Driver: WGHGAC50 - hni>": "Order.driver" must be a "CustomUser" instance.
    # drvier 가 CustomUser 참조하고 있음. 확인 필요
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="주문을 처리할 운전자"
    )
    

    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="주문을 처리할 운전자"
    )
    
    truck = models.ForeignKey(
        Truck,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        help_text="사용할 트럭"
    )
    chassis = models.ForeignKey(
        Chassis,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        help_text="사용할 샤시"
    )
    container = models.ForeignKey(
        Container,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        help_text="사용할 컨테이너"
    )
    trailer = models.ForeignKey(
        Trailer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        help_text="사용할 트레일러"
    )
    departure_yard = models.ForeignKey(
        Yard,
        on_delete=models.PROTECT,
        related_name='departure_orders',
        help_text="출발 야드"
    )
    arrival_yard = models.ForeignKey(
        Yard,
        on_delete=models.PROTECT,
        related_name='arrival_orders',
        help_text="도착 야드"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text="주문의 상태"
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text="주문 처리 중 발생한 에러 메시지"
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text="주문 생성 시간")
    updated_at = models.DateTimeField(auto_now=True, help_text="주문 수정 시간")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "주문"
        verbose_name_plural = "주문들"

    def __str__(self):
        return f"Order {self.id} by {self.driver.username}"
