# apps/yms_view/admin.py

from django.contrib import admin
from .models import Transaction
from apps.yms_edit.models import Truck, Chassis, Container, Trailer

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'equipment_type', 'get_equipment_serial_number', 'departure_yard', 'arrival_yard', 'movement_time')
    list_filter = ('equipment_type', 'departure_yard', 'arrival_yard', 'movement_time')
    search_fields = ('equipment', 'departure_yard__yard_id', 'arrival_yard__yard_id')

    def get_equipment_serial_number(self, obj):
        if obj.equipment_type == 'Truck':
            truck = Truck.objects.filter(id=obj.equipment).first()
            return truck.serial_number if truck else 'Unknown'
        elif obj.equipment_type == 'Chassis':
            chassis = Chassis.objects.filter(id=obj.equipment).first()
            return chassis.serial_number if chassis else 'Unknown'
        elif obj.equipment_type == 'Container':
            container = Container.objects.filter(id=obj.equipment).first()
            return container.serial_number if container else 'Unknown'
        elif obj.equipment_type == 'Trailer':
            trailer = Trailer.objects.filter(id=obj.equipment).first()
            return trailer.serial_number if trailer else 'Unknown'
        else:
            return 'N/A'
    get_equipment_serial_number.short_description = 'Equipment Serial Number'
