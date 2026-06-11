from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'role', 'is_approved_organizer', 'city', 'is_staff']
    list_filter = ['role', 'is_approved_organizer', 'is_staff', 'is_superuser']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'is_approved_organizer', 'phone', 'city', 'profile_picture')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'is_approved_organizer', 'phone', 'city', 'profile_picture')}),
    )

admin.site.register(User, CustomUserAdmin)

