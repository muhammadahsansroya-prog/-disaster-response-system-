from django.contrib import admin
from .models import HelpRequest, Resource, DispatchLog

@admin.register(HelpRequest)
class HelpRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'victim_name', 'location', 'urgency', 'status', 'created_at')
    list_filter = ('urgency', 'status')
    search_fields = ('victim_name', 'location')

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')

@admin.register(DispatchLog)
class DispatchLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'resource', 'dispatched_at')