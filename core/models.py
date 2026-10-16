from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ======================================================================
# ROLES — one profile per logged-in user, built on Django's auth User
# ======================================================================
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('VICTIM', 'Victim / Citizen'),
        ('ADMIN', 'System Administrator'),
        ('RESPONDER', 'Field Responder'),
        ('RESOURCE_UNIT', 'Resource Unit'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='VICTIM')
    phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


# ======================================================================
# EXISTING MODELS — kept exactly as they are so current data is safe.
# Only new fields are appended (all optional, so old rows stay valid).
# ======================================================================
class Department(models.Model):
    name = models.CharField(max_length=100)
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

    PRIORITY_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]

    # Extended status list — old values (PENDING, ASSIGNED_TO_DEPT, IN_PROGRESS,
    # RESOLVED, REJECTED) are kept so existing rows remain valid.
    STATUS_CHOICES = [
        ('PENDING', 'Submitted - Pending Admin Review'),
        ('UNDER_REVIEW', 'Under Review'),
        ('VERIFIED', 'Verified'),
        ('ASSIGNED_TO_DEPT', 'Assigned to Field Department'),
        ('ASSIGNED', 'Assigned to Responder'),
        ('RESPONDER_ACCEPTED', 'Responder Accepted'),
        ('RESOURCE_SEARCH', 'Searching for Resource'),
        ('RESOURCE_ALLOCATED', 'Resource Allocated'),
        ('DISPATCHED', 'Dispatched'),
        ('IN_PROGRESS', 'Responder & Resource Deployed'),
        ('ARRIVED', 'Arrived at Location'),
        ('ASSISTANCE_PROVIDED', 'Assistance Provided'),
        ('RESOLVED', 'Completed & Safely Resolved'),
        ('CANCELLED', 'Cancelled by Victim'),
        ('REJECTED', 'Cancelled / Invalid Alert'),
    ]

    DISASTER_TYPES = [
        ('Medical Emergency', 'Medical Emergency / Ambulance'),
        ('Flood Relief', 'Flood Relief / Water Rescue'),
        ('Fire Emergency', 'Fire Emergency'),
        ('Food & Shelter', 'Food, Water & Shelter Request'),
        ('Earthquake Rescue', 'Earthquake Building Collapse'),
        ('Landslide', 'Landslide'),
        ('Storm', 'Severe Storm'),
        ('General Rescue', 'General Rescue / Hazmat'),
        ('Other', 'Other'),
    ]

    # ---- original fields (unchanged) ----
    victim_name = models.CharField(max_length=150, default="Anonymous")
    victim_phone = models.CharField(max_length=20, blank=True, null=True, default="")
    need_type = models.CharField(max_length=100, choices=DISASTER_TYPES, default='Medical Emergency')
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='medium')
    description = models.TextField(blank=True, null=True, help_text="Detailed emergency description")
    location = models.CharField(max_length=255, help_text="Street / Area Address")
    latitude = models.FloatField(default=30.6514)
    longitude = models.FloatField(default=73.1306)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    assigned_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_responder = models.CharField(max_length=150, blank=True, null=True, default="Unassigned")
    allocated_resource = models.CharField(max_length=150, blank=True, null=True, default="None")
    admin_instructions = models.TextField(blank=True, null=True)
    progress_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ---- new fields (all optional — existing rows stay valid) ----
    victim_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='submitted_requests',
                                     help_text="Linked account if the victim is logged in")
    alternate_phone = models.CharField(max_length=20, blank=True, null=True)
    cnic = models.CharField(max_length=20, blank=True, null=True, help_text="Optional")
    affected_people = models.PositiveIntegerField(default=1)
    children_count = models.PositiveIntegerField(default=0)
    elderly_count = models.PositiveIntegerField(default=0)
    injured_count = models.PositiveIntegerField(default=0)
    missing_count = models.PositiveIntegerField(default=0)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    severity = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='medium',
                                 help_text="Disaster severity as reported by victim")
    incident_time = models.DateTimeField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=50, blank=True, null=True)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    assigned_responder_profile = models.ForeignKey('ResponderTeam', on_delete=models.SET_NULL,
                                                     null=True, blank=True, related_name='assigned_requests')
    is_demo = models.BooleanField(default=False)

    def __str__(self):
        return f"Req #{self.id} - {self.victim_name} ({self.need_type})"

    @property
    def google_maps_url(self):
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"

    def auto_priority(self):
        """Suggest a priority from the data already captured. Admin/responder can override."""
        if self.injured_count > 0 or self.missing_count > 0 or self.urgency == 'critical':
            return 'CRITICAL'
        if self.urgency == 'high':
            return 'HIGH'
        if self.urgency == 'low':
            return 'LOW'
        return 'MEDIUM'


class RequiredResourceType(models.Model):
    """A single requirement line on a request, e.g. 'Ambulance x1'."""
    RESOURCE_TYPES = [
        ('Medical Assistance', 'Medical Assistance'),
        ('Ambulance', 'Ambulance'),
        ('Rescue Team', 'Rescue Team'),
        ('Food', 'Food'),
        ('Drinking Water', 'Drinking Water'),
        ('Shelter', 'Shelter'),
        ('Rescue Boat', 'Rescue Boat'),
        ('Fire & Rescue', 'Fire & Rescue'),
        ('Evacuation', 'Evacuation'),
        ('Medicines', 'Medicines'),
        ('Blood', 'Blood'),
        ('Emergency Transport', 'Emergency Transport'),
        ('Search & Rescue', 'Search & Rescue'),
        ('Other', 'Other'),
    ]
    request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE, related_name='required_resources')
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPES)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.resource_type} x{self.quantity} for Req #{self.request_id}"


class Resource(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('BUSY', 'Deployed / Busy'),
        ('MAINTENANCE', 'Off Service'),
        ('DISPATCHED', 'Dispatched'),
        ('EN_ROUTE', 'En Route'),
        ('ON_SITE', 'On Site'),
        ('COMPLETED', 'Completed'),
        ('OFFLINE', 'Offline'),
    ]
    # ---- original fields (unchanged) ----
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='resources', null=True, blank=True)
    name = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    current_location = models.CharField(max_length=200, default="Central Station")

    # ---- new fields (optional) ----
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='resource_unit', help_text="Login account for this resource unit")
    organization = models.CharField(max_length=150, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.FloatField(default=30.6514)
    longitude = models.FloatField(default=73.1306)
    capacity = models.PositiveIntegerField(default=1)
    is_demo = models.BooleanField(default=False)

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


# ======================================================================
# NEW WORKFLOW MODELS
# ======================================================================
class ResponderTeam(models.Model):
    AVAILABILITY_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('BUSY', 'Busy'),
        ('OFFLINE', 'Offline'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='responder_team')
    team_name = models.CharField(max_length=150)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.FloatField(default=30.6514)
    longitude = models.FloatField(default=73.1306)
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='AVAILABLE')
    is_demo = models.BooleanField(default=False)

    def __str__(self):
        return self.team_name


class Assignment(models.Model):
    STATUS_CHOICES = [
        ('ASSIGNED', 'Assigned'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
    ]
    request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE, related_name='assignments')
    responder = models.ForeignKey(ResponderTeam, on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    instructions = models.TextField(blank=True, null=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ASSIGNED')

    def __str__(self):
        return f"Assignment: Req #{self.request_id} -> {self.responder.team_name}"


class ResourceAllocation(models.Model):
    STATUS_CHOICES = [
        ('ALLOCATED', 'Allocated'),
        ('ACCEPTED', 'Accepted'),
        ('DISPATCHED', 'Dispatched'),
        ('EN_ROUTE', 'En Route'),
        ('ARRIVED', 'Arrived'),
        ('ASSISTANCE_PROVIDED', 'Assistance Provided'),
        ('COMPLETED', 'Completed'),
    ]
    request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE, related_name='allocations')
    responder = models.ForeignKey(ResponderTeam, on_delete=models.SET_NULL, null=True, blank=True)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='allocations')
    allocated_at = models.DateTimeField(auto_now_add=True)
    dispatch_time = models.DateTimeField(null=True, blank=True)
    completion_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='ALLOCATED')

    def __str__(self):
        return f"Allocation: {self.resource.name} -> Req #{self.request_id}"


class ProgressReport(models.Model):
    request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE, related_name='progress_reports')
    resource = models.ForeignKey(Resource, on_delete=models.SET_NULL, null=True, blank=True)
    responder = models.ForeignKey(ResponderTeam, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=30)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Update on Req #{self.request_id}: {self.message[:40]}"

    class Meta:
        ordering = ['-timestamp']


class Notification(models.Model):
    TYPE_CHOICES = [
        ('REQUEST_SUBMITTED', 'Request Submitted'),
        ('REQUEST_VERIFIED', 'Request Verified'),
        ('RESPONDER_ASSIGNED', 'Responder Assigned'),
        ('RESOURCE_ALLOCATED', 'Resource Allocated'),
        ('STATUS_CHANGED', 'Status Changed'),
        ('REQUEST_COMPLETED', 'Request Completed'),
        ('NEW_ASSIGNMENT', 'New Assignment'),
        ('PROGRESS_UPDATE', 'Progress Update'),
        ('CRITICAL_ALERT', 'Critical Alert'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=150)
    message = models.TextField()
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    related_request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE, null=True, blank=True)
    read_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.user.username}: {self.title}"

    class Meta:
        ordering = ['-created_at']


class DisasterEvent(models.Model):
    """Used for the public 'Pakistan disaster situations' section on the homepage."""
    SEVERITY_CHOICES = [
        ('CRITICAL', 'Critical'), ('HIGH', 'High'), ('MEDIUM', 'Medium'), ('LOW', 'Low'),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'), ('MONITORING', 'Monitoring'), ('RESOLVED', 'Resolved'),
    ]
    disaster_type = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=200)
    latitude = models.FloatField(default=30.6514)
    longitude = models.FloatField(default=73.1306)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MEDIUM')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    is_demo = models.BooleanField(default=True, help_text="Mark as demo/sample data unless this is a verified real event")

    def __str__(self):
        return f"{self.title} ({self.get_severity_display()})"

    class Meta:
        ordering = ['-date']


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=200)
    affected_model = models.CharField(max_length=100, blank=True, null=True)
    affected_id = models.PositiveIntegerField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} - {self.action}"

    class Meta:
        ordering = ['-timestamp']