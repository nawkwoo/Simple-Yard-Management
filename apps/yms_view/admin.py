# apps/yms_view/admin.py

from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Transaction 모델을 위한 관리자 인터페이스 설정.
    """
    list_display = (
        'id',
        'equipment_type',
        'get_equipment',
        'departure_yard',
        'arrival_yard',
        'movement_time',
        'details'
    )
    list_filter = ('equipment_type', 'departure_yard', 'arrival_yard', 'movement_time')
    search_fields = ('truck__serial_number', 'chassis__serial_number', 'container__serial_number', 'trailer__serial_number', 'details')

    def get_equipment(self, obj):
        """
        선택된 장비 유형에 따라 장비를 표시합니다.
        """
        if obj.equipment_type == 'Truck' and obj.truck:
            return obj.truck.serial_number
        elif obj.equipment_type == 'Chassis' and obj.chassis:
            return obj.chassis.serial_number
        elif obj.equipment_type == 'Container' and obj.container:
            return obj.container.serial_number
        elif obj.equipment_type == 'Trailer' and obj.trailer:
            return obj.trailer.serial_number
        elif obj.equipment_type == 'PersonalVehicle':
            return "Personal Vehicle"
        return "N/A"
    get_equipment.short_description = '장비'
