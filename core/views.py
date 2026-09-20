from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import HelpRequest, Resource

def submit_request(request):
    if request.method == 'POST':
        HelpRequest.objects.create(
            location=request.POST.get('location'),
            latitude=request.POST.get('latitude') or 33.6844,
            longitude=request.POST.get('longitude') or 73.0479,
            need_type=request.POST.get('need_type'),
            urgency=request.POST.get('urgency'),
        )
        return render(request, 'core/success.html')

    return render(request, 'core/submit_request.html')


@login_required
def responder_dashboard(request):
    my_resources = Resource.objects.filter(responder=request.user)
    return render(request, 'core/responder_dashboard.html', {'resources': my_resources})