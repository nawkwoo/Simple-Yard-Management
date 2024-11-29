from django.db import models
from apps.yms_edit.models import Yard, Driver

class Order(models.Model):
    truck = models.CharField(max_length=10, blank=True, null=True)  # 트럭 ID
    chassis = models.CharField(max_length=10, blank=True, null=True)  # 샤시 ID
    container = models.CharField(max_length=15, blank=True, null=True)  # 컨테이너 ID
    trailer = models.CharField(max_length=15, blank=True, null=True)  # 트레일러 ID
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, related_name="orders")  # 운전자
    departure_time = models.DateTimeField()  # 출발 시간
    arrival_time = models.DateTimeField()  # 도착 시간
    departure_yard = models.ForeignKey(Yard, on_delete=models.SET_NULL, null=True, related_name="orders_departed")  # 출발 위치
    arrival_yard = models.ForeignKey(Yard, on_delete=models.SET_NULL, null=True, related_name="orders_arrived")  # 도착 위치

    def __str__(self):
        return f"Order {self.id}: {self.truck or 'No Truck'} -> {self.arrival_yard or 'Unknown'}"