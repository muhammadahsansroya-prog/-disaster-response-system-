from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Includes Password Reset, Login & Auth routes
    path('', include('core.urls')),                          # Core Application Routes
]