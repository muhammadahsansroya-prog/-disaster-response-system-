from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import HelpRequest, Resource, DispatchLog, Department, UserProfile


def home(request):
    """Home Landing Page — public, no login needed"""
    return render(request, 'core/home.html')


def signup_view(request):
    """Personnel / Responder Registration View"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        father_name = request.POST.get('father_name', '').strip()
        cnic = request.POST.get('cnic', '').strip()
        province = request.POST.get('province', '')
        district = request.POST.get('district', '').strip()
        city = request.POST.get('city', '').strip()
        address = request.POST.get('address', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        mobile_number = request.POST.get('mobile_number', '').strip()
        emergency_contact = request.POST.get('emergency_contact', '').strip()

        # Basic Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'core/signup.html')

        if User.objects.filter(username=cnic).exists():
            messages.error(request, "An account with this CNIC already exists!")
            return render(request, 'core/signup.html')

        try:
            # Create User (using CNIC as username for uniqueness)
            user = User.objects.create_user(
                username=cnic,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Create or update UserProfile with additional fields
            UserProfile.objects.create(
                user=user,
                father_name=father_name,
                cnic=cnic,
                province=province,
                district=district,
                city=city,
                address=address,
                postal_code=postal_code,
                mobile_number=mobile_number,
                emergency_contact=emergency_contact,
                role='RESPONDER'
            )

            messages.success(request, "Official Personnel Registration completed successfully! You can now log in.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")

    return render(request, 'core/signup.html')


def submit_request(request):
    """Victim Public Request Submission Portal — public, no login needed"""
    if request.method == 'POST':
        victim_name = request.POST.get('victim_name') or 'Anonymous'
        victim_phone = request.POST.get('victim_phone', '')
        need_type = request.POST.get('need_type') or 'General Rescue'
        urgency = request.POST.get('urgency') or 'medium'
        description = request.POST.get('description', '')
        location = request.POST.get('location') or 'Location Not Provided'

        try:
            latitude = float(request.POST.get('latitude', 30.6514))
            longitude = float(request.POST.get('longitude', 73.1306))
        except ValueError:
            latitude, longitude = 30.6514, 73.1306

        req = HelpRequest.objects.create(
            victim_name=victim_name,
            victim_phone=victim_phone,
            need_type=need_type,
            urgency=urgency,
            description=description,
            location=location,
            latitude=latitude,
            longitude=longitude,
            status='PENDING'
        )

        DispatchLog.objects.create(
            help_request=req,
            action_by='Victim (Public User)',
            status_update='PENDING',
            notes=f"Emergency Alert Created by {victim_name} ({victim_phone}). Location: {location}"
        )

        messages.success(request, f"Emergency Alert #{req.id} submitted! Central Dispatch team has been alerted.")
        return redirect('submit_request')

    return render(request, 'core/submit_request.html')


@login_required
def dispatch_dashboard(request):
    """System Administrator Central Command Center — ADMIN ONLY"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "You do not have permission to access the Admin Command Center.")
        return redirect('home')

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')

        if request_id:
            help_req = get_object_or_404(HelpRequest, id=request_id)

            if action == 'assign_dept':
                dept_id = request.POST.get('department_id')
                responder_unit = request.POST.get('assigned_responder', 'Field Unit')
                instructions = request.POST.get('admin_instructions', '')

                dept = Department.objects.filter(id=dept_id).first() if dept_id else None

                help_req.status = 'ASSIGNED_TO_DEPT'
                help_req.assigned_department = dept
                help_req.assigned_responder = responder_unit
                help_req.admin_instructions = instructions
                help_req.save()

                DispatchLog.objects.create(
                    help_request=help_req,
                    action_by='System Administrator',
                    status_update='ASSIGNED_TO_DEPT',
                    notes=f"Assigned to {dept.name if dept else 'Department'} ({responder_unit}). Notes: {instructions}"
                )
                messages.success(request, f"Request #{help_req.id} forwarded to {responder_unit}.")

            elif action == 'resolve':
                help_req.status = 'RESOLVED'
                help_req.save()

                DispatchLog.objects.create(
                    help_request=help_req,
                    action_by='System Administrator',
                    status_update='RESOLVED',
                    notes="Request closed & marked as resolved by Admin."
                )
                messages.success(request, f"Request #{help_req.id} closed successfully.")

        return redirect('dispatch_dashboard')

    help_requests = HelpRequest.objects.all().order_by('-created_at')
    departments = Department.objects.all()
    logs = DispatchLog.objects.all().order_by('-dispatched_at')[:25]

    context = {
        'help_requests': help_requests,
        'departments': departments,
        'logs': logs,
    }
    return render(request, 'core/dispatch_dashboard.html', context)


@login_required
def responder_dashboard(request):
    """Field Responder & Resource Deployment Hub — RESPONDER (or ADMIN) ONLY"""
    is_admin = request.user.is_staff or request.user.is_superuser
    is_responder = False
    try:
        is_responder = request.user.profile.role == 'RESPONDER'
    except Exception:
        is_responder = False

    if not (is_admin or is_responder):
        messages.error(request, "You do not have permission to access the Field Responder panel.")
        return redirect('home')

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        allocated_resource = request.POST.get('allocated_resource', 'Field Unit')
        new_status = request.POST.get('status', 'IN_PROGRESS')
        progress_notes = request.POST.get('progress_notes', '')

        if request_id:
            help_req = get_object_or_404(HelpRequest, id=request_id)
            help_req.status = new_status
            help_req.allocated_resource = allocated_resource
            if progress_notes:
                help_req.progress_notes = progress_notes
            help_req.save()

            DispatchLog.objects.create(
                help_request=help_req,
                resource_name=allocated_resource,
                action_by='Field Responder Team',
                status_update=new_status,
                notes=f"Resource Allocated: {allocated_resource}. Status: {new_status}. Notes: {progress_notes}"
            )
            messages.success(request, f"Request #{help_req.id} updated to {new_status} with {allocated_resource}.")

        return redirect('responder_dashboard')

    assigned_requests = HelpRequest.objects.exclude(status='RESOLVED').order_by('-created_at')
    resources = Resource.objects.all()

    context = {
        'assigned_requests': assigned_requests,
        'resources': resources,
    }
    return render(request, 'core/responder_dashboard.html', context)