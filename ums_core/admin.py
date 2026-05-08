from django.contrib.admin import AdminSite

class CustomAdminSite(AdminSite):
    """Custom admin site with automatic CSS loading."""
    site_header = 'University Management System'
    site_title = 'UMS Admin'
    index_title = 'Welcome to UMS Administration'
    
    def each_context(self, request):
        context = super().each_context(request)
        # Add custom CSS to all admin pages
        context['site_css'] = [
            'admin/custom_admin.css',
        ]
        return context

# Create custom admin site instance
admin_site = CustomAdminSite(name='admin')
