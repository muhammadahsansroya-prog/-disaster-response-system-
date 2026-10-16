from django.contrib import admin
from .models import (
    Department, HelpRequest, Resource, DispatchLog, UserProfile,
    ResponderTeam, Assignment, ResourceAllocation, ProgressReport,
    Notification, DisasterEvent, AuditLog, RequiredResourceType,
)

admin.site.register(Department)
admin.site.register(HelpRequest)
admin.site.register(Resource)
admin.site.register(DispatchLog)
admin.site.register(UserProfile)
admin.site.register(ResponderTeam)
admin.site.register(Assignment)
admin.site.register(ResourceAllocation)
admin.site.register(ProgressReport)
admin.site.register(Notification)
admin.site.register(DisasterEvent)
admin.site.register(AuditLog)
admin.site.register(RequiredResourceType)