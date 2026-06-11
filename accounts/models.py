from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('ORGANIZER', 'Organizer'),
        ('CUSTOMER', 'Customer'),
    )
    
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='CUSTOMER')
    is_approved_organizer = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin_role(self):
        return self.role == 'ADMIN' or self.is_superuser
        
    @property
    def is_organizer_role(self):
        return self.role == 'ORGANIZER'
        
    @property
    def is_customer_role(self):
        return self.role == 'CUSTOMER'
