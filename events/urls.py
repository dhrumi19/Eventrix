from django.urls import path
from . import views

urlpatterns = [
    # Customer / User Module URLs
    path('', views.home_view, name='home'),
    path('event/<int:event_id>/', views.event_detail_view, name='event_detail'),
    path('event/<int:event_id>/select-seats/', views.select_seats_view, name='select_seats'),
    path('booking/<int:booking_id>/pay/', views.payment_view, name='payment'),
    path('payment/callback/', views.payment_callback_view, name='payment_callback'),
    path('booking/<int:booking_id>/success/', views.booking_success_view, name='booking_success'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking_view, name='cancel_booking'),
    path('ticket/<str:ticket_code>/', views.view_ticket_qr_view, name='view_ticket_qr'),
    path('ticket/<str:ticket_code>/pdf/', views.download_ticket_pdf_view, name='download_ticket_pdf'),
    path('notification/<int:notification_id>/read/', views.read_notification_view, name='read_notification'),

    # Organizer Module URLs
    path('organizer/create-event/', views.create_event_view, name='create_event'),
    path('organizer/edit-event/<int:event_id>/', views.edit_event_view, name='edit_event'),
    path('organizer/delete-event/<int:event_id>/', views.delete_event_view, name='delete_event'),
    path('organizer/setup-seats/<int:event_id>/', views.setup_seats_view, name='setup_seats'),
    path('organizer/bookings/<int:event_id>/', views.organizer_bookings_view, name='organizer_bookings'),
    path('organizer/export-participants/<int:event_id>/<str:export_type>/', views.export_participants_view, name='export_participants'),

    # Admin Module URLs
    path('admin-panel/approve-organizer/<int:user_id>/', views.approve_organizer_view, name='approve_organizer'),
    path('admin-panel/delete-user/<int:user_id>/', views.delete_user_admin_view, name='delete_user_admin'),
    path('admin-panel/approve-event/<int:event_id>/', views.approve_event_view, name='approve_event'),
    path('admin-panel/reject-event/<int:event_id>/', views.reject_event_view, name='reject_event'),
    path('admin-panel/report/pdf/<str:report_type>/', views.admin_report_pdf_view, name='admin_report_pdf'),
    path('admin-panel/report/excel/<str:report_type>/', views.admin_report_excel_view, name='admin_report_excel'),
]
