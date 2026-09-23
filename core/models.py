from django.db import models
from django.contrib.auth.models import User

class HelpRequest(models.Model):
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Level 1 Critical'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Dispatch'),
        ('matched', 'Matched With Unit'),
        ('dispatched', 'Rescue Unit Dispatched'),
        ('completed', 'Evacuated / Completed'),
        ('cancelled', 'Cancelled'),
    ]

    DISASTER_TYPES = [
        ('flood', 'Flash Flood Evacuation'),
        ('medical', 'Medical Emergency / Casualty'),
        ('ration', 'PM Food & Water Supply'),
        ('collapse', 'Structural Collapse Rescue'),
    ]

    victim = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='help_requests')
    victim_name = models.CharField(max_length=150, help_text="Citizen Name / Contact Person")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    disaster_type = models.CharField(max_length=50, choices=DISASTER_TYPES, default='flood')
    need_type = models.CharField(max_length=100, help_text="e.g. 15 Stranded, Medical Kit needed")
    people_affected = models.PositiveIntegerField(default=1)
    
    # Geographic Location Data
    location = models.CharField(max_length=255, help_text="City, Sector, or Landmark")
    latitude = models.FloatField(default=30.6682)  # Punjab Default Center (Sahiwal HQ)
    longitude = models.FloatField(default=73.1114)
    
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tracking_code = models.CharField(max_length=20, unique=True, blank=True, null=True, help_text="Unique PM Relief Tracking ID")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_urgency_display()}] {self.victim_name} - {self.need_type} ({self.get_status_display()})"


class Resource(models.Model):
    RESOURCE_TYPES = [
        ('food', 'PM Food Ration Packs'),
        ('water', 'Clean Drinking Water'),
        ('medical', 'Medical Emergency Team / Kits'),
        ('rescue_boat', 'Rescue Boats & Life Vests'),
        ('shelter', 'Temporary Relief Tents'),
        ('helicopter', 'Aerial Air-Drop Unit'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available in Warehouse'),
        ('in_use', 'Partially Dispatched'),
        ('dispatched', 'Fully Dispatched'),
        ('depleted', 'Out of Stock'),
    ]

    title = models.CharField(max_length=150, help_text="e.g. Sahiwal Relief Warehouse Pack-A")
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    quantity = models.PositiveIntegerField(default=100, help_text="Current available items/units")
    total_capacity = models.PositiveIntegerField(default=500, help_text="Total capacity of depot")
    unit_type = models.CharField(max_length=20, default='Packs', help_text="e.g. Packs, Liters, Boats, Kits")
    
    # Depot / Warehouse Location
    depot_name = models.CharField(max_length=255, default="Central Depot Sahiwal")
    location = models.CharField(max_length=255)
    latitude = models.FloatField(default=30.6682)
    longitude = models.FloatField(default=73.1114)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    responder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_resources')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_resource_type_display()} ({self.quantity} {self.unit_type}) - {self.depot_name}"


class DispatchLog(models.Model):
    help_request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE, related_name='dispatch_logs')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='dispatch_logs')
    dispatched_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="Dispatcher Admin/Command Official")
    quantity_allocated = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True, null=True, help_text="Special instructions for field taskforce")
    dispatched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-dispatched_at']

    def __str__(self):
        return f"PM Relief Dispatch #{self.id}: {self.resource.get_resource_type_display()} -> {self.help_request.victim_name}"