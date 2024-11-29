# apps/dashboard/admin.py

from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'truck', 'chassis', 'container', 'trailer', 'driver', 'departure_yard', 'arrival_yard', 'departure_time', 'arrival_time', 'status')
    list_filter = ('status', 'departure_yard', 'arrival_yard', 'departure_time', 'arrival_time')
    search_fields = ('truck__serial_number', 'chassis__serial_number', 'container__serial_number', 'trailer__serial_number', 'driver__driver_id', 'driver__user__username')
