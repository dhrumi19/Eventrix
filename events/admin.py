from django.contrib import admin
from .models import Event, Seat, Booking, Payment, Ticket, Notification, Report

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'city', 'ticket_price', 'capacity', 'organizer', 'is_approved', 'is_published', 'date_time']
    list_filter = ['category', 'is_approved', 'is_published', 'city', 'date_time']
    search_fields = ['title', 'venue', 'organizer__username']
    actions = ['approve_events', 'publish_events']

    def approve_events(self, request, queryset):
        queryset.update(is_approved=True)
    approve_events.short_description = "Mark selected events as Approved"

    def publish_events(self, request, queryset):
        queryset.update(is_published=True)
    publish_events.short_description = "Mark selected events as Published"

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['event', 'row_label', 'seat_number', 'status', 'booked_by']
    list_filter = ['status', 'row_label', 'event']
    search_fields = ['event__title', 'booked_by__username']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event', 'total_amount', 'payment_status', 'booking_date']
    list_filter = ['payment_status', 'booking_date', 'event']
    search_fields = ['user__username', 'event__title']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'payment_id', 'order_id', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['payment_id', 'order_id', 'booking__id']

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['booking', 'ticket_code', 'created_at']
    search_fields = ['ticket_code', 'booking__id']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'message']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['report_type', 'generated_by', 'created_at']
    list_filter = ['report_type', 'created_at']
    search_fields = ['generated_by__username']

