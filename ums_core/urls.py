"""UMS URL Configuration."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),  # Django Jet Reboot
    path('admin/', admin.site.urls),
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
