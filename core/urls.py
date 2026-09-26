from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('submit/', views.submit_request, name='submit_request'),
    path('responder/', views.responder_dashboard, name='responder_dashboard'),
    path('dispatch/', views.dispatch_dashboard, name='dispatch_dashboard'),
    path('update-status/<int:request_id>/', views.update_request_status, name='update_request_status'),
    path('chatbot/', views.chatbot_reply, name='chatbot_reply'),

    # Auth URLs
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', views.signup, name='signup'),  # Naya user account banane ke liye
]