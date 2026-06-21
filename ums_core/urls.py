"""UMS URL Configuration."""
from django.contrib import admin
from django.urls import path, include
from . import admin as ums_admin
from django.contrib import admin as django_admin
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# Build admin URL list with our db-tools view included so it's available
# under the 'admin' namespace for reverse('admin:db_tools')
admin_urls = [
    path('db-tools/', django_admin.site.admin_view(ums_admin.db_tools_view), name='db_tools'),
]
admin_urls += django_admin.site.get_urls()

urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),  # Django Jet Reboot
    path('admin/', include((admin_urls, 'admin'), namespace='admin')),
    path('', include('accounts.urls')),
    path('students/', include('students.urls')),
    path('academics/', include('academics.urls')),
    path('staff/', include('staff.urls')),
    path('finance/', include('finance.urls')),
    path('library/', include('library.urls')),
    path('hostel/', include('hostel.urls')),
    path('communications/', include('communications.urls')),
    path('reports/', include('reports.urls')),
    # API endpoints
    path('api/accounts/', include('accounts.api_urls')),
    path('api/students/', include('students.api_urls')),
    path('api/academics/', include('academics.api_urls')),
    path('api/finance/', include('finance.api_urls')),
    path('api/staff/', include('staff.api_urls')),
    path('api/communications/', include('communications.api_urls')),
    # API Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "University Management System"
admin.site.site_title = "UMS Admin"
admin.site.index_title = "Administration"
