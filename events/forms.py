from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('title', 'description', 'category', 'city', 'venue', 'date_time', 'ticket_price', 'capacity', 'banner', 'is_published')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-glass', 'placeholder': 'Event Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-glass', 'rows': 4, 'placeholder': 'Event Description'}),
            'category': forms.Select(attrs={'class': 'form-select form-control-glass'}),
            'city': forms.TextInput(attrs={'class': 'form-control form-control-glass', 'placeholder': 'e.g. Mumbai, Delhi, Bangalore'}),
            'venue': forms.TextInput(attrs={'class': 'form-control form-control-glass', 'placeholder': 'Venue Address'}),
            'date_time': forms.DateTimeInput(attrs={'class': 'form-control form-control-glass', 'type': 'datetime-local'}),
            'ticket_price': forms.NumberInput(attrs={'class': 'form-control form-control-glass', 'placeholder': 'Price in INR', 'step': '0.01'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control form-control-glass', 'placeholder': 'Total Capacity'}),
            'banner': forms.FileInput(attrs={'class': 'form-control form-control-glass'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
