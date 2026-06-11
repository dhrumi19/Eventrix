from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone
from .models import User
from .forms import UserRegistrationForm, UserProfileUpdateForm
from events.models import Event, Booking, Seat, Payment, Notification

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data.get('role')
            user.role = role
            if role == 'ORGANIZER':
                user.is_approved_organizer = False  # requires admin approval
                user.save()
                messages.success(request, "Registration successful! Since you registered as an Organizer, your account is pending Admin approval. You will be notified once approved.")
                return redirect('login')
            else:
                user.is_approved_organizer = True
                user.save()
                login(request, user)
                messages.success(request, f"Welcome to Eventrix, {user.username}! Your account has been created.")
                return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            # Retrieve 'next' redirect URL and ensure it's safe (local path)
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
                
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def dashboard_view(request):
    if request.user.is_admin_role:
        return redirect('admin_dashboard')
    elif request.user.is_organizer_role:
        return redirect('organizer_dashboard')
    else:
        return redirect('customer_dashboard')


@login_required
def customer_dashboard_view(request):
    if request.user.role != 'CUSTOMER':
        return redirect('dashboard')
    
    # Bookings made by user
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    
    # Upcoming bookings
    now = timezone.now()
    upcoming_bookings = bookings.filter(event__date_time__gte=now, payment_status='COMPLETED')
    
    # Booking history
    past_bookings = bookings.filter(event__date_time__lt=now) | bookings.exclude(payment_status='COMPLETED')
    
    # Unread notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'notifications': notifications,
    }
    return render(request, 'accounts/customer_dashboard.html', context)


@login_required
def organizer_dashboard_view(request):
    if not request.user.is_organizer_role:
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard')
        
    if not request.user.is_approved_organizer:
        return render(request, 'accounts/organizer_pending.html')
        
    my_events = Event.objects.filter(organizer=request.user)
    
    # Summary Cards
    total_events = my_events.count()
    
    # Total tickets sold for my events
    my_event_ids = my_events.values_list('id', flat=True)
    total_bookings = Booking.objects.filter(event_id__in=my_event_ids, payment_status='COMPLETED')
    
    # Tickets Sold
    total_tickets_sold = sum(b.seats.count() for b in total_bookings)
    
    # Total Revenue
    total_revenue_agg = Payment.objects.filter(booking__event_id__in=my_event_ids, booking__payment_status='COMPLETED').aggregate(sum_amount=Sum('amount'))
    total_revenue = total_revenue_agg['sum_amount'] or 0
    
    # Occupancy rate: booked seats / total seat capacity
    total_capacity = my_events.aggregate(sum_cap=Sum('capacity'))['sum_cap'] or 0
    occupancy_rate = 0
    if total_capacity > 0:
        occupancy_rate = round((total_tickets_sold / total_capacity) * 100, 2)

    # Event-wise Revenue details
    event_revenue_list = []
    for event in my_events:
        eb = Booking.objects.filter(event=event, payment_status='COMPLETED')
        t_sold = sum(b.seats.count() for b in eb)
        e_rev = Payment.objects.filter(booking__event=event, booking__payment_status='COMPLETED').aggregate(sum_amount=Sum('amount'))['sum_amount'] or 0
        occ = round((t_sold / event.capacity) * 100, 2) if event.capacity > 0 else 0
        event_revenue_list.append({
            'event': event,
            'tickets_sold': t_sold,
            'revenue': e_rev,
            'occupancy': occ
        })
        
    # Notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    context = {
        'total_events': total_events,
        'total_tickets_sold': total_tickets_sold,
        'total_revenue': total_revenue,
        'occupancy_rate': occupancy_rate,
        'event_revenue_list': event_revenue_list,
        'notifications': notifications,
    }
    return render(request, 'accounts/organizer_dashboard.html', context)


@login_required
def admin_dashboard_view(request):
    if not request.user.is_admin_role:
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard')
        
    # Summary Metrics
    total_users = User.objects.filter(role='CUSTOMER').count()
    total_organizers = User.objects.filter(role='ORGANIZER').count()
    total_events = Event.objects.count()
    total_bookings = Booking.objects.filter(payment_status='COMPLETED').count()
    
    total_revenue_agg = Payment.objects.filter(status='SUCCESS').aggregate(sum_amount=Sum('amount'))
    total_revenue = total_revenue_agg['sum_amount'] or 0
    
    # Pending approvals
    pending_organizers = User.objects.filter(role='ORGANIZER', is_approved_organizer=False)
    pending_events = Event.objects.filter(is_approved=False)
    
    # Notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    context = {
        'total_users': total_users,
        'total_organizers': total_organizers,
        'total_events': total_events,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'pending_organizers': pending_organizers,
        'pending_events': pending_events,
        'notifications': notifications,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in
            messages.success(request, "Your password was successfully updated!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})
