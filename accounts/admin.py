from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User, AuditLog
from .widgets import GroupedPermissionsWidget


class BaseAdmin(admin.ModelAdmin):
    """Base admin class that removes related field buttons globally"""
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        # Remove all related field buttons (add, change, delete, view)
        if hasattr(formfield.widget, 'can_add_related'):
            formfield.widget.can_add_related = False
        if hasattr(formfield.widget, 'can_change_related'):
            formfield.widget.can_change_related = False
        if hasattr(formfield.widget, 'can_delete_related'):
            formfield.widget.can_delete_related = False
        if hasattr(formfield.widget, 'can_view_related'):
            formfield.widget.can_view_related = False
        return formfield

    class Media:
        css = {
            'all': ('admin/custom_admin.css',)
        }


class CustomUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'user_permissions' in self.fields:
            self.fields['user_permissions'].widget = GroupedPermissionsWidget()


class CustomUserCreationForm(UserCreationForm):
    pass


@admin.register(User)
class CustomUserAdmin(BaseAdmin, UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    fieldsets = (
        ('GENERAL', {'fields': ('username', 'password'), 'classes': ('tab-general',)}),
        ('PERSONAL INFO', {'fields': ('first_name', 'last_name', 'email'), 'classes': ('tab-personal',)}),
        ('PERMISSIONS', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions',
            ),
            'classes': ('tab-permissions',),
        }),
        ('UMS Profile', {
            'fields': ('role', 'phone_number', 'date_of_birth', 'gender',
                      'address', 'profile_picture', 'is_active_member')
        }),
        ('IMPORTANT DATES', {'fields': ('last_login', 'date_joined'), 'classes': ('tab-important',)}),
    )

    add_fieldsets = (
        ('GENERAL', {
            'classes': ('tab-general',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('PERSONAL INFO', {
            'classes': ('tab-personal',),
            'fields': ('first_name', 'last_name', 'email'),
        }),
        ('PERMISSIONS', {
            'classes': ('tab-permissions',),
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('UMS Profile', {
            'fields': ('role', 'phone_number', 'date_of_birth', 'gender',
                      'address', 'profile_picture', 'is_active_member')
        }),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'gender']
    search_fields = ['username', 'email', 'first_name', 'last_name']


@admin.register(AuditLog)
class AuditLogAdmin(BaseAdmin):
    list_display = ['user', 'action', 'model_name', 'timestamp']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'action', 'details']
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'details', 'ip_address', 'timestamp']
