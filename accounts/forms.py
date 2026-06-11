from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=(('CUSTOMER', 'User (Book Tickets)'), ('ORGANIZER', 'Organizer (Manage Events)')),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select form-control-glass'})
    )
    phone = forms.CharField(required=False, max_length=15)
    city = forms.CharField(required=False, max_length=100)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'role', 'phone', 'city')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'role':
                field.widget.attrs['class'] = 'form-control form-control-glass'
                field.widget.attrs['placeholder'] = f"Enter {field.label}"


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'city', 'profile_picture')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-glass', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-glass', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-glass', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-glass', 'placeholder': 'Phone Number'}),
            'city': forms.TextInput(attrs={'class': 'form-control form-control-glass', 'placeholder': 'City'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control form-control-glass'}),
        }
