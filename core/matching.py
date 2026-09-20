import math
from .models import Resource

def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula - do coordinates ke beech ka distance (km mein) nikalta hai
    R = 6371  # Earth ka radius km mein
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon/2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


def find_nearest_resource(help_request):
    available_resources = Resource.objects.filter(status='available')

    nearest = None
    shortest_distance = None

    for resource in available_resources:
        distance = calculate_distance(
            help_request.latitude, help_request.longitude,
            resource.latitude, resource.longitude
        )
        if shortest_distance is None or distance < shortest_distance:
            shortest_distance = distance
            nearest = resource

    return nearest, shortest_distance