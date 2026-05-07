from django.contrib import admin
from accounts.admin import BaseAdmin
from .models import Hostel, Room, RoomAllocation, MaintenanceRequest


@admin.register(Hostel)
class HostelAdmin(BaseAdmin):
    list_display = ['code', 'name', 'hostel_type', 'total_rooms', 'total_capacity', 'is_active']
    list_filter = ['hostel_type', 'is_active']


@admin.register(Room)
class RoomAdmin(BaseAdmin):
    list_display = ['hostel', 'room_number', 'room_type', 'capacity', 'current_occupancy', 'is_available']
    list_filter = ['hostel', 'room_type', 'is_available']


@admin.register(RoomAllocation)
class RoomAllocationAdmin(BaseAdmin):
    list_display = ['student', 'room', 'session', 'is_active', 'allocation_date']
    list_filter = ['session', 'is_active']


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(BaseAdmin):
    list_display = ['room', 'issue', 'priority', 'status', 'created_at']
    list_filter = ['priority', 'status']
