# apps/dashboard/models.py

from django.db import models
from apps.yms_edit.models import Yard, Driver, Truck, Chassis, Container, Trailer

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    truck = models.ForeignKey(Truck, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')  # 트럭 객체 참조
    chassis = models.ForeignKey(Chassis, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    container = models.ForeignKey(Container, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    trailer = models.ForeignKey(Trailer, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, related_name="orders")  # 운전자
    departure_time = models.DateTimeField()  # 출발 시간
    arrival_time = models.DateTimeField()  # 도착 시간
    departure_yard = models.ForeignKey(Yard, on_delete=models.SET_NULL, null=True, related_name="orders_departed")  # 출발 위치
    arrival_yard = models.ForeignKey(Yard, on_delete=models.SET_NULL, null=True, related_name="orders_arrived")  # 도착 위치
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')  # 주문 상태
    error_message = models.TextField(blank=True, null=True)  # 오류 메시지 (선택 사항)

    def __str__(self):
        truck_serial = self.truck.serial_number if self.truck else 'No Truck'
        arrival_yard_id = self.arrival_yard.yard_id if self.arrival_yard else 'Unknown'
        return f"Order {self.id}: {truck_serial} -> {arrival_yard_id}"
