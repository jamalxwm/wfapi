from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('id', 'username', 'email')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    # Fieldsets for edit page
    fieldsets = (
        (None, {'fields': ('username', 'id')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    

# Now we just have to register our custom UserAdmin
admin.site.register(User, UserAdmin)