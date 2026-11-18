from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, ConsentRecord


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Дополнительно', {'fields': ('full_name', 'phone')}),)
    list_display = ('email', 'full_name', 'is_staff')


admin.site.register(UserProfile)
admin.site.register(ConsentRecord)