from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core import mail
from accounts.models import User
from events.models import Event, Seat, Booking, Payment, Ticket, Notification
import datetime

# Compatibility Patch for Django 4.2 on Python 3.14.x
# The test runner copies Context objects which fails on Python 3.14 due to changes in super() copy methods.
from django.template.context import Context
def patched_context_copy(self):
    duplicate = Context(self)
    duplicate.dicts = self.dicts[:]
    return duplicate
Context.__copy__ = patched_context_copy


class EventrixTestCases(TestCase):
    def setUp(self):
        # Create test users
        self.admin_user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpassword',
            role='ADMIN',
            is_approved_organizer=True
        )
        
        self.organizer_user = User.objects.create_user(
            username='testorg',
            email='org@test.com',
            password='testpassword',
            role='ORGANIZER',
            is_approved_organizer=True
        )
        
        self.customer_user = User.objects.create_user(
            username='testcustomer',
            email='customer@test.com',
            password='testpassword',
            role='CUSTOMER'
        )
        
        # Create a test event
        self.event = Event.objects.create(
            title='Test Concert',
            description='Test description of the concert.',
            category='MUSIC',
            city='Mumbai',
            venue='Test Arena',
            date_time=timezone.now() + datetime.timedelta(days=2),
            ticket_price=1000.00,
            capacity=10,
            organizer=self.organizer_user,
            is_published=True,
            is_approved=True
        )
        
        # Generate seats A1 to A5
        self.seats = []
        for i in range(1, 6):
            self.seats.append(
                Seat.objects.create(
                    event=self.event,
                    row_label='A',
                    seat_number=i,
                    status='AVAILABLE'
                )
            )

    def test_custom_user_roles(self):
        """Test user role property properties."""
        self.assertTrue(self.admin_user.is_admin_role)
        self.assertTrue(self.organizer_user.is_organizer_role)
        self.assertTrue(self.customer_user.is_customer_role)
        self.assertFalse(self.customer_user.is_admin_role)

    def test_event_discovery_view(self):
        """Test exploring events list and applying city filtering."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Concert')
        
        # Filter by city
        response_city = self.client.get(reverse('home'), {'city': 'Mumbai'})
        self.assertEqual(response_city.status_code, 200)
        self.assertContains(response_city, 'Test Concert')
        
        # Filter by non-existing city
        response_fake_city = self.client.get(reverse('home'), {'city': 'Pune'})
        self.assertEqual(response_fake_city.status_code, 200)
        self.assertNotContains(response_fake_city, 'Test Concert')

    def test_seat_availability(self):
        """Verify seats counts are accurate."""
        self.assertEqual(self.event.available_seats_count, 5)

    def test_unauthorized_dashboard_access(self):
        """Dashboard path must redirect to login if unauthenticated."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_seat_selection_booking_creation(self):
        """Log in as customer, choose seats A1 and A2, and check booking total."""
        self.client.login(username='testcustomer', password='testpassword')
        
        selected_seat_ids = [self.seats[0].id, self.seats[1].id]
        response = self.client.post(
            reverse('select_seats', kwargs={'event_id': self.event.id}),
            {'selected_seats': selected_seat_ids}
        )
        
        # Should redirect to payment checkout screen
        self.assertEqual(response.status_code, 302)
        
        # Assert booking is generated in database
        booking = Booking.objects.get(user=self.customer_user, event=self.event)
        self.assertEqual(booking.payment_status, 'PENDING')
        self.assertEqual(booking.total_amount, 2000.00) # 2 seats x 1000.00
        
        # Verify seats are blocked temporarily
        self.seats[0].refresh_from_db()
        self.seats[1].refresh_from_db()
        self.assertEqual(self.seats[0].status, 'BLOCKED')
        self.assertEqual(self.seats[1].status, 'BLOCKED')

    def test_payment_success_callback(self):
        """Verify successful payment callback completes booking, locks seats, and spawns ticket files."""
        # Create a pending booking first
        booking = Booking.objects.create(
            user=self.customer_user,
            event=self.event,
            total_amount=1000.00,
            payment_status='PENDING'
        )
        booking.seats.add(self.seats[0])
        self.seats[0].status = 'BLOCKED'
        self.seats[0].booked_by = self.customer_user
        self.seats[0].save()
        
        self.client.login(username='testcustomer', password='testpassword')
        
        response = self.client.post(reverse('payment_callback'), {
            'booking_id': booking.id,
            'status': 'success',
            'razorpay_payment_id': 'pay_test123',
            'razorpay_order_id': 'ord_test123',
            'razorpay_signature': 'sig_test123'
        })
        
        # Assert redirect to success page
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('booking_success', kwargs={'booking_id': booking.id}), response.url)
        
        # Refresh and verify
        booking.refresh_from_db()
        self.assertEqual(booking.payment_status, 'COMPLETED')
        
        self.seats[0].refresh_from_db()
        self.assertEqual(self.seats[0].status, 'BOOKED')
        
        # Verify ticket, payment logs and QR exist
        ticket = Ticket.objects.get(booking=booking)
        self.assertIsNotNone(ticket.ticket_code)
        self.assertTrue(Payment.objects.filter(booking=booking, status='SUCCESS').exists())

        # Verify email was sent and has correct details & attachment
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, [self.customer_user.email])
        self.assertIn(ticket.ticket_code, sent_email.body)
        self.assertEqual(len(sent_email.attachments), 1)
        self.assertEqual(sent_email.attachments[0][0], f"ticket_{ticket.ticket_code}.pdf")

    def test_booking_success_view(self):
        """Test that booking success page loads details correctly."""
        booking = Booking.objects.create(
            user=self.customer_user,
            event=self.event,
            total_amount=1000.00,
            payment_status='COMPLETED'
        )
        ticket = Ticket.objects.create(booking=booking)
        
        self.client.login(username='testcustomer', password='testpassword')
        response = self.client.get(reverse('booking_success', kwargs={'booking_id': booking.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Booking Confirmed!')
        self.assertContains(response, self.event.title)
        self.assertContains(response, ticket.ticket_code)

    def test_cancel_booking_action(self):
        """Test that a user can cancel a confirmed booking, releasing seats and deleting the ticket."""
        booking = Booking.objects.create(
            user=self.customer_user,
            event=self.event,
            total_amount=1000.00,
            payment_status='COMPLETED'
        )
        ticket = Ticket.objects.create(booking=booking)
        self.seats[0].status = 'BOOKED'
        self.seats[0].booked_by = self.customer_user
        self.seats[0].save()
        booking.seats.add(self.seats[0])
        
        self.client.login(username='testcustomer', password='testpassword')
        response = self.client.post(reverse('cancel_booking', kwargs={'booking_id': booking.id}))
        self.assertEqual(response.status_code, 302)
        
        # Verify seats are released
        self.seats[0].refresh_from_db()
        self.assertEqual(self.seats[0].status, 'AVAILABLE')
        self.assertIsNone(self.seats[0].booked_by)
        
        # Verify ticket is deleted
        self.assertFalse(Ticket.objects.filter(booking=booking).exists())
        
        # Verify booking status is updated to CANCELLED
        booking.refresh_from_db()
        self.assertEqual(booking.payment_status, 'CANCELLED')


class EventReminderTestCases(TestCase):
    def setUp(self):
        from django.core.management import call_command
        self.call_command = call_command
        
        # Create user
        self.user = User.objects.create_user(
            username='reminduser',
            email='remind@test.com',
            password='testpassword',
            role='CUSTOMER'
        )
        
        # Create organizer
        self.organizer = User.objects.create_user(
            username='remindorg',
            email='remindorg@test.com',
            password='testpassword',
            role='ORGANIZER',
            is_approved_organizer=True
        )
        
    def test_reminders_triggered_correctly(self):
        # We need three events:
        # 1. Today
        # 2. In 3 days
        # 3. In 2 days (should not get reminders)
        # 4. In 4 days (should not get reminders)
        
        today_date = timezone.localdate()
        
        # Event today
        event_today = Event.objects.create(
            title='Concert Today',
            description='Concert Happening Today',
            category='MUSIC',
            city='Mumbai',
            venue='Today Arena',
            date_time=timezone.make_aware(datetime.datetime.combine(today_date, datetime.time(19, 0))),
            ticket_price=100.00,
            capacity=10,
            organizer=self.organizer,
            is_published=True,
            is_approved=True
        )
        
        # Event in 3 days
        event_3days = Event.objects.create(
            title='Concert In 3 Days',
            description='Concert Happening In 3 Days',
            category='MUSIC',
            city='Mumbai',
            venue='3-Days Arena',
            date_time=timezone.make_aware(datetime.datetime.combine(today_date + datetime.timedelta(days=3), datetime.time(19, 0))),
            ticket_price=100.00,
            capacity=10,
            organizer=self.organizer,
            is_published=True,
            is_approved=True
        )
        
        # Event in 2 days
        event_2days = Event.objects.create(
            title='Concert In 2 Days',
            description='Concert Happening In 2 Days',
            category='MUSIC',
            city='Mumbai',
            venue='2-Days Arena',
            date_time=timezone.make_aware(datetime.datetime.combine(today_date + datetime.timedelta(days=2), datetime.time(19, 0))),
            ticket_price=100.00,
            capacity=10,
            organizer=self.organizer,
            is_published=True,
            is_approved=True
        )
        
        # Create bookings for these events
        booking_today = Booking.objects.create(
            user=self.user,
            event=event_today,
            total_amount=100.00,
            payment_status='COMPLETED'
        )
        
        booking_3days = Booking.objects.create(
            user=self.user,
            event=event_3days,
            total_amount=100.00,
            payment_status='COMPLETED'
        )
        
        booking_2days = Booking.objects.create(
            user=self.user,
            event=event_2days,
            total_amount=100.00,
            payment_status='COMPLETED'
        )
        
        # Clear outbox
        mail.outbox = []
        
        # Run command
        self.call_command('send_event_reminders')
        
        # Assert database updates
        booking_today.refresh_from_db()
        booking_3days.refresh_from_db()
        booking_2days.refresh_from_db()
        
        self.assertTrue(booking_today.reminder_today_sent)
        self.assertFalse(booking_today.reminder_3days_sent)
        
        self.assertTrue(booking_3days.reminder_3days_sent)
        self.assertFalse(booking_3days.reminder_today_sent)
        
        self.assertFalse(booking_2days.reminder_today_sent)
        self.assertFalse(booking_2days.reminder_3days_sent)
        
        # Verify in-app notifications
        notifications = list(Notification.objects.filter(user=self.user).order_by('created_at'))
        self.assertEqual(len(notifications), 2)
        
        # One for today, one for 3 days
        msg_today = f"Reminder: Your event 'Concert Today' is TODAY at 07:00 PM!"
        msg_3days = f"Reminder: You have an upcoming event 'Concert In 3 Days' on {(today_date + datetime.timedelta(days=3)).strftime('%d %b %Y')} at 07:00 PM."
        
        messages = [n.message for n in notifications]
        self.assertIn(msg_today, messages)
        self.assertIn(msg_3days, messages)
        
        # Verify email notifications sent
        self.assertEqual(len(mail.outbox), 2)
        subjects = [email.subject for email in mail.outbox]
        self.assertIn("[Reminder] Your event 'Concert Today' is TODAY!", subjects)
        self.assertIn("[Reminder] Upcoming event: 'Concert In 3 Days' in 3 days!", subjects)
        
        # Run command again - no new reminders should be sent
        mail.outbox = []
        self.call_command('send_event_reminders')
        self.assertEqual(len(mail.outbox), 0)

