from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import HelpRequest, Resource

def submit_request(request):
    if request.method == 'POST':
        need_type = request.POST.get('disaster_type') or request.POST.get('need_type')
        location = request.POST.get('location')
        latitude = request.POST.get('latitude') or 33.6844
        longitude = request.POST.get('longitude') or 73.0479
        urgency = request.POST.get('urgency') or 'high'

        HelpRequest.objects.create(
            location=location,
            latitude=latitude,
            longitude=longitude,
            need_type=need_type,
            urgency=urgency,
        )
        
        messages.success(request, "Emergency alert submitted successfully! Dispatch team has been notified.")
        return redirect('submit_request')

    return render(request, 'core/submit_request.html')


@login_required
def responder_dashboard(request):
    my_resources = Resource.objects.filter(responder=request.user)
    return render(request, 'core/responder_dashboard.html', {'resources': my_resources})