from django.db import models
from django.contrib.auth.models import User

# Emergency Request Model
class HelpRequest(models.Model):
    victim_name = models.CharField(max_length=100, default='Anonymous')
    location = models.CharField(max_length=255)
    urgency = models.CharField(max_length=50, default='HIGH')
    status = models.CharField(max_length=50, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'victim_help_requests'

    def __str__(self):
        return f"{self.victim_name} - {self.location} ({self.status})"


# Resource Model
class Resource(models.Model):
    name = models.CharField(max_length=100, db_column='name', default='General Resource')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'resource_depots'

    def __str__(self):
        return self.name


# Dispatch Log Model
class DispatchLog(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    dispatched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-dispatched_at']

    def __str__(self):
        return f"Dispatch #{self.id}"