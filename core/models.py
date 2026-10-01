from django.db import models
from django.utils import timezone


class Department(models.Model):
    name = models.CharField(max_length=100)  # e.g., Rescue 1122, Fire Brigade, Medical Response, Food & Shelter
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class HelpRequest(models.Model):
    URGENCY_CHOICES = [
        ('low', 'Low - Informational'),
        ('medium', 'Medium - Urgent Needs'),
        ('high', 'High - Severe Situation'),
        ('critical', 'CRITICAL - Life Threatening'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Admin Review'),
        ('ASSIGNED_TO_DEPT', 'Assigned to Field Department'),
        ('IN_PROGRESS', 'Responder & Resource Deployed'),
        ('RESOLVED', 'Completed & Safely Resolved'),
        ('REJECTED', 'Cancelled / Invalid Alert'),
    ]

    DISASTER_TYPES = [
        ('Medical Emergency', 'Medical Emergency / Ambulance'),
        ('Flood Relief', 'Flood Relief / Water Rescue'),
        ('Fire Emergency', 'Fire Emergency'),
        ('Food & Shelter', 'Food, Water & Shelter Request'),
        ('Earthquake Rescue', 'Earthquake Building Collapse'),
        ('General Rescue', 'General Rescue / Hazmat'),
    ]

    # Victim / User Info
    victim_name = models.CharField(max_length=150, default="Anonymous")
    victim_phone = models.CharField(max_length=20, blank=True, null=True, default="")
    need_type = models.CharField(max_length=100, choices=DISASTER_TYPES, default='Medical Emergency')
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='medium')
    description = models.TextField(blank=True, null=True, help_text="Detailed emergency description")

    # Location & Live Map Coordinates
    location = models.CharField(max_length=255, help_text="Street / Area Address")
    latitude = models.FloatField(default=30.6514)
    longitude = models.FloatField(default=73.1306)

    # Workflow & Tracking Fields
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    assigned_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_responder = models.CharField(max_length=150, blank=True, null=True, default="Unassigned")
    allocated_resource = models.CharField(max_length=150, blank=True, null=True, default="None")
    admin_instructions = models.TextField(blank=True, null=True)
    progress_notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Req #{self.id} - {self.victim_name} ({self.need_type})"

    @property
    def google_maps_url(self):
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"


class Resource(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='resources', null=True, blank=True)
    name = models.CharField(max_length=100)  # e.g., Ambulance Unit #102, Fire Truck #4
    resource_type = models.CharField(max_length=50)  # Vehicle, Equipment, Personnel
    status = models.CharField(max_length=20, choices=[('AVAILABLE', 'Available'), ('BUSY', 'Deployed / Busy'), ('MAINTENANCE', 'Off Service')], default='AVAILABLE')
    current_location = models.CharField(max_length=200, default="Central Station")

    def __str__(self):
        return f"{self.name} ({self.status})"


class DispatchLog(models.Model):
    help_request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE, related_name='logs')
    resource_name = models.CharField(max_length=100, blank=True, null=True, default="N/A")
    action_by = models.CharField(max_length=100, default='System Administrator')
    status_update = models.CharField(max_length=50, default='PENDING')
    notes = models.TextField(blank=True, null=True)
    dispatched_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Log #{self.id} for Request #{self.help_request_id} [{self.status_update}]"