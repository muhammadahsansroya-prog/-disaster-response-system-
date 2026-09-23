from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Direct /accounts/login/ to your custom template so it never crashes
    path('accounts/login/', auth_views.LoginView.as_view(template_name='core/login.html')),
    path('', include('core.urls')),
]