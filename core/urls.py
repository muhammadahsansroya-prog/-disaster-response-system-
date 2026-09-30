from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('responder/', views.responder_dashboard, name='responder_dashboard'),
    path('dispatch/', views.dispatch_dashboard, name='dispatch_dashboard'),
    path('submit/', views.submit_request, name='submit_request'),
    path('update_status/<int:request_id>/', views.update_request_status, name='update_request_status'),
]