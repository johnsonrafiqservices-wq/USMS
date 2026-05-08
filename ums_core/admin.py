from django.contrib.admin import AdminSite

class CustomAdminSite(AdminSite):
    """Custom admin site with automatic CSS loading."""
    site_header = 'University Management System'
    site_title = 'UMS Admin'
    index_title = 'Welcome to UMS Administration'

# Create custom admin site instance
admin_site = CustomAdminSite(name='admin')
