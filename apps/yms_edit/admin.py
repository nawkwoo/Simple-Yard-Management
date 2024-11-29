from django.contrib import admin
from .models import YardInventory

@admin.register(YardInventory)
class YardInventoryAdmin(admin.ModelAdmin):
    list_display = ('yard', 'equipment_type', 'equipment_id', 'is_available')