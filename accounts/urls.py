from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/customer/', views.customer_dashboard_view, name='customer_dashboard'),
    path('dashboard/organizer/', views.organizer_dashboard_view, name='organizer_dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
]
