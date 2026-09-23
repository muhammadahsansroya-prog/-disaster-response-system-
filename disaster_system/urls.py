from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Force /accounts/login/ to use your custom template instead of registration/login.html
    path('accounts/login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='accounts_login'),
    
    # Built-in Auth URLs (Password Reset, Password Change, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Core Application URLs
    path('', include('core.urls')),
]