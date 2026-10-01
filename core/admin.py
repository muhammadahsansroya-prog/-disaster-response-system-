from django.contrib import admin
from .models import HelpRequest, Resource, DispatchLog, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    search_fields = ('name', 'code')


@admin.register(HelpRequest)
class HelpRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'victim_name', 'need_type', 'urgency', 'status', 'created_at')
    list_filter = ('status', 'urgency', 'need_type')
    search_fields = ('victim_name', 'victim_phone', 'location')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'department', 'resource_type', 'status', 'current_location')
    list_filter = ('status', 'resource_type', 'department')
    search_fields = ('name', 'current_location')


@admin.register(DispatchLog)
class DispatchLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'help_request', 'action_by', 'status_update', 'dispatched_at')
    list_filter = ('status_update', 'dispatched_at')
    search_fields = ('notes', 'action_by')