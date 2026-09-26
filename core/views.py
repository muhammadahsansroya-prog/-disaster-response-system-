from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import HelpRequest, Resource, DispatchLog, ChatLog
from .chatbot import get_bot_response, get_session_id


def home(request):
    """Central Home Landing Page View"""
    return render(request, 'core/index.html')


def submit_request(request):
    if request.method == 'POST':
        need_type = request.POST.get('disaster_type') or request.POST.get('need_type')
        location = request.POST.get('location')
        latitude = request.POST.get('latitude') or 33.6844
        longitude = request.POST.get('longitude') or 73.0479
        urgency = request.POST.get('urgency') or 'medium'

        HelpRequest.objects.create(
            location=location,
            latitude=latitude,
            longitude=longitude,
            need_type=need_type,
            urgency=urgency,
            status='pending'
        )

        messages.success(request, "Emergency alert submitted successfully! Dispatch team has been notified.")
        return redirect('submit_request')

    return render(request, 'core/submit_request.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('responder_dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})


@login_required
def responder_dashboard(request):
    my_resources = Resource.objects.filter(responder=request.user)
    requests = HelpRequest.objects.all().order_by('-created_at')
    return render(request, 'core/responder_dashboard.html', {
        'resources': my_resources,
        'requests': requests
    })


@login_required
def update_request_status(request, request_id):
    if request.method == 'POST':
        help_request = get_object_or_404(HelpRequest, id=request_id)
        new_status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in HelpRequest.STATUS_CHOICES]

        if new_status in valid_statuses:
            help_request.status = new_status
            help_request.save()
            messages.success(request, f"Status updated to '{new_status.title()}' successfully.")

    return redirect('responder_dashboard')


@login_required
def dispatch_dashboard(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        resource_id = request.POST.get('resource_id')

        help_req = get_object_or_404(HelpRequest, id=request_id)
        resource = get_object_or_404(Resource, id=resource_id)

        DispatchLog.objects.create(help_request=help_req, resource=resource)

        help_req.status = 'dispatched'
        help_req.save()

        resource.status = 'dispatched'
        resource.save()

        messages.success(request, f"Resource '{resource.resource_type}' assigned to {help_req.need_type} request successfully!")
        return redirect('dispatch_dashboard')

    requests = HelpRequest.objects.all().order_by('-created_at')
    resources = Resource.objects.all()
    dispatch_logs = DispatchLog.objects.all().order_by('-dispatched_at')

    return render(request, 'core/dispatch_dashboard.html', {
        'requests': requests,
        'resources': resources,
        'dispatch_logs': dispatch_logs
    })


@csrf_exempt
def chatbot_reply(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        session_id = get_session_id(request)
        bot_response = get_bot_response(user_message)

        ChatLog.objects.create(
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_response
        )
        return JsonResponse({'response': bot_response})

    return JsonResponse({'error': 'POST required'}, status=400)

