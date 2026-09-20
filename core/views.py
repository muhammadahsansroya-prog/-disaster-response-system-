from django.shortcuts import render, redirect
from .models import HelpRequest

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