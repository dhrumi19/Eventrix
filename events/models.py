from django.db import models
from django.conf import settings
import uuid

class Event(models.Model):
    CATEGORY_CHOICES = (
        ('MUSIC', 'Music'),
        ('COMEDY', 'Comedy'),
        ('THEATRE', 'Theatre & Arts'),
        ('SPORTS', 'Sports'),
        ('CONFERENCE', 'Conferences & Tech'),
        ('OTHER', 'Other'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='OTHER')
    city = models.CharField(max_length=100)
    venue = models.CharField(max_length=250)
    date_time = models.DateTimeField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()
    banner = models.ImageField(upload_to='event_banners/', blank=True, null=True)
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_events')
    is_published = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def available_seats_count(self):
        return self.seats.filter(status='AVAILABLE').count()


class Seat(models.Model):
    STATUS_CHOICES = (
        ('AVAILABLE', 'Available'),
        ('BOOKED', 'Booked'),
        ('BLOCKED', 'Blocked'),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='seats')
    row_label = models.CharField(max_length=5) # e.g. 'A', 'B'
    seat_number = models.IntegerField()       # e.g. 1, 2, 3
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='AVAILABLE')
    booked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reserved_seats')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event', 'row_label', 'seat_number')
        ordering = ['row_label', 'seat_number']

    def __str__(self):
        return f"{self.event.title} - {self.row_label}{self.seat_number} ({self.status})"


class Booking(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    seats = models.ManyToManyField(Seat, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    reminder_3days_sent = models.BooleanField(default=False)
    reminder_today_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking #{self.id} by {self.user.username} for {self.event.title}"


class Payment(models.Model):
    STATUS_CHOICES = (
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    payment_id = models.CharField(max_length=100) # Razorpay Payment ID
    order_id = models.CharField(max_length=100)   # Razorpay Order ID
    signature = models.CharField(max_length=250, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='SUCCESS')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.payment_id} for Booking #{self.booking.id} ({self.status})"


class Ticket(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='ticket')
    ticket_code = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    qr_code = models.ImageField(upload_to='tickets/qr/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='tickets/pdf/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket {self.ticket_code} for Booking #{self.booking.id}"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}..."


class Report(models.Model):
    REPORT_TYPE_CHOICES = (
        ('REVENUE', 'Revenue Report'),
        ('BOOKING', 'Booking Report'),
        ('EVENT', 'Event Report'),
        ('PARTICIPANT', 'Participant Report'),
    )

    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    file = models.FileField(upload_to='reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_report_type_display()} generated at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
