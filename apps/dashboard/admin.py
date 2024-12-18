# apps/dashboard/admin.py

from django.contrib import admin
from django.conf import settings
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Order 모델을 위한 관리자 인터페이스 설정.
    """
    list_display = (
        'id', 
        'driver', 
        'truck', 
        'chassis', 
        'container', 
        'trailer', 
        'departure_yard', 
        'arrival_yard', 
        'status'
    )
    list_filter = ('status', 'departure_yard', 'arrival_yard', 'driver')
    search_fields = (
        'driver__username', 
        'truck__truck_id', 
        'chassis__chassis_id', 
        'container__container_id', 
        'trailer__trailer_id'
    )

    # 필드 정렬 순서 개선
    ordering = ('-id',)
