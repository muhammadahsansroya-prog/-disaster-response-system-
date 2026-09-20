from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('submit/', views.submit_request, name='submit_request'),
    path('responder/', views.responder_dashboard, name='responder_dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]