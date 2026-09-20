from django.contrib import admin
from .models import HelpRequest, Resource, DispatchLog
from .matching import find_nearest_resource

@admin.action(description="Dispatch nearest available resource")
def dispatch_nearest(modeladmin, request, queryset):
    for help_request in queryset:
        resource, distance = find_nearest_resource(help_request)
        if resource:
            DispatchLog.objects.create(help_request=help_request, resource=resource)
            resource.status = 'dispatched'
            resource.save()
            help_request.status = 'dispatched'
            help_request.save()
            modeladmin.message_user(request, f"{resource} dispatched ({distance:.1f} km away) for request #{help_request.id}")
        else:
            modeladmin.message_user(request, f"No available resource found for request #{help_request.id}", level='warning')


class HelpRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'need_type', 'location', 'urgency', 'status', 'created_at')
    actions = [dispatch_nearest]


admin.site.register(HelpRequest, HelpRequestAdmin)
admin.site.register(Resource)
admin.site.register(DispatchLog)