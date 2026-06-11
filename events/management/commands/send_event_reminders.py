import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Booking, Notification
from events.utils import send_reminder_email

class Command(BaseCommand):
    help = 'Sends email and notification reminders to users for events happening today or in 3 days.'

    def handle(self, *args, **options):
        today = timezone.localdate()
        three_days_from_now = today + datetime.timedelta(days=3)

        self.stdout.write(f"Running send_event_reminders on {today}...")

        # 1. 3-day reminders
        bookings_3days = Booking.objects.filter(
            payment_status='COMPLETED',
            event__date_time__date=three_days_from_now,
            reminder_3days_sent=False
        )
        
        sent_3days = 0
        for booking in bookings_3days:
            # Send Email
            email_success = send_reminder_email(booking, days_left=3)
            
            # Create In-app Notification
            local_dt = timezone.localtime(booking.event.date_time)
            formatted_time = local_dt.strftime('%I:%M %p')
            formatted_date = local_dt.strftime('%d %b %Y')
            msg = f"Reminder: You have an upcoming event '{booking.event.title}' on {formatted_date} at {formatted_time}."
            
            Notification.objects.create(
                user=booking.user,
                message=msg
            )
            
            # Mark reminder as sent
            booking.reminder_3days_sent = True
            booking.save()
            
            sent_3days += 1
            self.stdout.write(f"Sent 3-day reminder to {booking.user.username} for event {booking.event.title}")

        # 2. Today's reminders
        bookings_today = Booking.objects.filter(
            payment_status='COMPLETED',
            event__date_time__date=today,
            reminder_today_sent=False
        )
        
        sent_today = 0
        for booking in bookings_today:
            # Send Email
            email_success = send_reminder_email(booking, days_left=0)
            
            # Create In-app Notification
            local_dt = timezone.localtime(booking.event.date_time)
            formatted_time = local_dt.strftime('%I:%M %p')
            msg = f"Reminder: Your event '{booking.event.title}' is TODAY at {formatted_time}!"
            
            Notification.objects.create(
                user=booking.user,
                message=msg
            )
            
            # Mark reminder as sent
            booking.reminder_today_sent = True
            booking.save()
            
            sent_today += 1
            self.stdout.write(f"Sent same-day reminder to {booking.user.username} for event {booking.event.title}")

        self.stdout.write(self.style.SUCCESS(
            f"Successfully processed reminders. Sent {sent_3days} 3-day reminders, and {sent_today} same-day reminders."
        ))
