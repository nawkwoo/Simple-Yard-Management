# apps/yms_edit/admin.py

from django.contrib import admin
from .models import (
    Division, Yard, YardInventory, Site,
    Truck, Chassis, Container, Trailer
)


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    """
    Division 모델을 위한 관리자 인터페이스 설정.
    """
    list_display = ('name', 'full_name')
    search_fields = ('name', 'full_name')


@admin.register(Yard)
class YardAdmin(admin.ModelAdmin):
    """
    Yard 모델을 위한 관리자 인터페이스 설정.
    """
    list_display = ('yard_id', 'division')
    search_fields = ('yard_id', 'division__name', 'division__full_name')
    list_filter = ('division',)


@admin.register(YardInventory)
class YardInventoryAdmin(admin.ModelAdmin):
    """
    YardInventory 모델을 위한 관리자 인터페이스 설정.
    """
    list_display = ('equipment_type', 'equipment_id', 'is_available', 'yard')
    search_fields = ('equipment_type', 'equipment_id', 'yard__yard_id')
    list_filter = ('equipment_type', 'is_available', 'yard')


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    """
    Site 모델을 위한 관리자 인터페이스 설정.
    """
    list_display = ('yard', 'equipment_type', 'capacity')
    search_fields = ('yard__yard_id', 'equipment_type')
    list_filter = ('equipment_type', 'yard')


@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    """
    Truck 모델을 위한 관리자 인터페이스 설정.
    """
    list_display = ('truck_id', 'serial_number', 'site', 'is_occupied')
    search_fields = ('truck_id', 'serial_number', 'site__yard__yard_id')
    list_filter = ('site__yard__division', 'is_occupied')


@admin.register(Chassis)
class ChassisAdmin(admin.ModelAdmin):
    """
    Chassis 모델을 위한 관리자 인터페이스 설정.
    """
    list_display = ('chassis_id', 'serial_number', 'type', 'site', 'is_occupied')
    search_fields = ('chassis_id', 'serial_number', 'site__yard__yard_id', 'type')
    list_filter = ('type', 'site__yard__division', 'is_occupied')


@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    """
    Container 모델을 위한 관리자 인터페이스 설정.
    """
    list_display = ('container_id', 'serial_number', 'size', 'type', 'site', 'is_occupied')
    search_fields = ('container_id', 'serial_number', 'site__yard__yard_id', 'size', 'type')
    list_filter = ('size', 'type', 'site__yard__division', 'is_occupied')


@admin.register(Trailer)
class TrailerAdmin(admin.ModelAdmin):
    """
    Trailer 모델을 위한 관리자 인터페이스 설정.
    """
    list_display = ('trailer_id', 'serial_number', 'size', 'site', 'is_occupied')
    search_fields = ('trailer_id', 'serial_number', 'site__yard__yard_id', 'size')
    list_filter = ('size', 'site__yard__division', 'is_occupied')
