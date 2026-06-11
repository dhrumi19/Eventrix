import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventrix.settings')
django.setup()

from accounts.models import User
from events.models import Event, Seat

def seed_database():
    print("Seeding database...")
    
    # 1. Create Users
    # Admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@eventrix.com',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
            'is_approved_organizer': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("Admin user created (admin / admin123)")
    else:
        print("Admin user already exists")

    # Organizer
    organizer_user, created = User.objects.get_or_create(
        username='organizer',
        defaults={
            'email': 'organizer@eventrix.com',
            'role': 'ORGANIZER',
            'is_approved_organizer': True
        }
    )
    if created:
        organizer_user.set_password('organizer123')
        organizer_user.save()
        print("Organizer user created (organizer / organizer123)")
    else:
        print("Organizer user already exists")

    # Customer
    customer_user, created = User.objects.get_or_create(
        username='customer',
        defaults={
            'email': 'customer@eventrix.com',
            'role': 'CUSTOMER'
        }
    )
    if created:
        customer_user.set_password('customer123')
        customer_user.save()
        print("Customer user created (customer / customer123)")
    else:
        print("Customer user already exists")

    # 2. Create Events
    events_data = [
        {
            'title': 'Sunburn Arena ft. DJ Nucleya',
            'description': 'Experience the ultimate music festival in your city! Nucleya brings the bass live with state-of-the-art visuals and sound systems. Don\'t miss out on this high-octane performance.',
            'category': 'MUSIC',
            'city': 'Mumbai',
            'venue': 'Jio Gardens, BKC',
            'ticket_price': 1499.00,
            'capacity': 50,
            'is_published': True,
            'is_approved': True,
            'days_ahead': 10
        },
        {
            'title': 'Comic Hour with Zakir Khan',
            'description': 'Get ready to laugh your lungs out as the legendary Zakir Khan comes to town with his brand new stand-up special. Real stories, honest humour, and unforgettable moments.',
            'category': 'COMEDY',
            'city': 'Delhi',
            'venue': 'Kamani Auditorium',
            'ticket_price': 999.00,
            'capacity': 40,
            'is_published': True,
            'is_approved': True,
            'days_ahead': 15
        },
        {
            'title': 'Global Tech Summit 2026',
            'description': 'Join key industry leaders, developers, and tech enthusiasts at the Global Tech Summit. Topics include Artificial Intelligence, Cloud Computing, and Web3 trends.',
            'category': 'CONFERENCE',
            'city': 'Bangalore',
            'venue': 'NIMHANS Convention Centre',
            'ticket_price': 1999.00,
            'capacity': 60,
            'is_published': True,
            'is_approved': True,
            'days_ahead': 20
        },
        {
            'title': 'IPL Final Fan Park',
            'description': 'Watch the ultimate clash on the giant screen! Complete stadium-like atmosphere, food stalls, and music to keep the vibes going. Perfect for friends and family.',
            'category': 'SPORTS',
            'city': 'Mumbai',
            'venue': 'National Sports Club of India',
            'ticket_price': 499.00,
            'capacity': 100,
            'is_published': True,
            'is_approved': True,
            'days_ahead': 5
        }
    ]

    for data in events_data:
        days = data.pop('days_ahead')
        event_time = timezone.now() + timedelta(days=days)
        
        event, created = Event.objects.get_or_create(
            title=data['title'],
            defaults={
                'description': data['description'],
                'category': data['category'],
                'city': data['city'],
                'venue': data['venue'],
                'date_time': event_time,
                'ticket_price': data['ticket_price'],
                'capacity': data['capacity'],
                'organizer': organizer_user,
                'is_published': data['is_published'],
                'is_approved': data['is_approved']
            }
        )
        if created:
            print(f"Created event: {event.title}")
            
            # Generate seats for the event
            # Standard grid: rows A to E (5 rows), seats 1 to 10 (10 seats per row) for capacity 50
            # We scale according to event capacity
            rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
            seats_per_row = 10
            total_seats_needed = min(event.capacity, 100)
            
            seats_created = 0
            for r in rows:
                if seats_created >= total_seats_needed:
                    break
                for s_num in range(1, seats_per_row + 1):
                    if seats_created >= total_seats_needed:
                        break
                    Seat.objects.create(
                        event=event,
                        row_label=r,
                        seat_number=s_num,
                        status='AVAILABLE'
                    )
                    seats_created += 1
            print(f"  Generated {seats_created} seats for '{event.title}'")
        else:
            print(f"Event '{data['title']}' already exists")

    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
