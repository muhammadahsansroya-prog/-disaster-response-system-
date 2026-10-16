from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('submit/', views.submit_request, name='submit_request'),
    path('dispatch/', views.dispatch_dashboard, name='dispatch_dashboard'),
    path('responder/', views.responder_dashboard, name='responder_dashboard'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
]