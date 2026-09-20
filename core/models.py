from django.db import models
from django.contrib.auth.models import User

class HelpRequest(models.Model):
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('matched', 'Matched'),
        ('dispatched', 'Dispatched'),
        ('completed', 'Completed'),
    ]

    victim = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    location = models.CharField(max_length=255)
    latitude = models.FloatField(default=33.6844)
    longitude = models.FloatField(default=73.0479)
    need_type = models.CharField(max_length=100)
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.need_type} - {self.location} ({self.status})"


class Resource(models.Model):
    RESOURCE_TYPES = [
        ('food', 'Food'),
        ('medical', 'Medical Team'),
        ('rescue_boat', 'Rescue Boat'),
        ('shelter', 'Shelter'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('dispatched', 'Dispatched'),
    ]

    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    location = models.CharField(max_length=255)
    latitude = models.FloatField(default=33.6844)
    longitude = models.FloatField(default=73.0479)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    responder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resources')

    def __str__(self):
        return f"{self.resource_type} at {self.location} ({self.status})"


class DispatchLog(models.Model):
    help_request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    dispatched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dispatch: {self.resource} -> {self.help_request}"