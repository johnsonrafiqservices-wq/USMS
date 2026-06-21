"""
Django settings for University Management System (UMS).
"""

from pathlib import Path
import os

try:
    from decouple import config, Csv
except ImportError:
    def config(key, default=None, cast=None):
        value = os.environ.get(key, default)
        if cast and value is not None:
            return cast(value)
        return value

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-ums-dev-key-change-in-production')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = ['*', '13.49.66.19', '192.168.100.179', '172.16.61.27', '172.16.61.102']

# Application definition
INSTALLED_APPS = [
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'drf_spectacular',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'crispy_forms',
    'crispy_bootstrap5',
    'import_export',
    # UMS Apps
    'accounts.apps.AccountsConfig',
    'students.apps.StudentsConfig',
    'academics.apps.AcademicsConfig',
    'staff.apps.StaffConfig',
    'finance.apps.FinanceConfig',
    'library.apps.LibraryConfig',
    'hostel.apps.HostelConfig',
    'communications.apps.CommunicationsConfig',
    'reports.apps.ReportsConfig',
    # Core app (provides admin DB tools, app config, and management commands)
    'ums_core.apps.UmsCoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.AuditLogMiddleware',
]

ROOT_URLCONF = 'ums_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.user_context',
                'accounts.context_processors.admin_dashboard_stats',
            ],
        },
    },
]

WSGI_APPLICATION = 'ums_core.wsgi.application'
ASGI_APPLICATION = 'ums_core.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
}

# CORS
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')

# Spectacular (Swagger/OpenAPI)
SPECTACULAR_SETTINGS = {
    'TITLE': 'University Management System API',
    'DESCRIPTION': 'REST API for UMS — students, academics, finance, staff, library, hostel, communications.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CONTACT': {'name': 'UMS Admin'},
    'LICENSE': {'name': 'Private'},
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {'format': '{levelname} {asctime} {message}', 'style': '{'},
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'ums.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {'handlers': ['console', 'file'], 'level': 'WARNING', 'propagate': True},
        'academics': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': False},
        'students': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': False},
        'finance': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': False},
    },
}

# Academic Settings
ACADEMIC_YEAR_START_MONTH = 9  # September
SEMESTERS_PER_YEAR = 2
MAX_CREDITS_PER_SEMESTER = 24
GPA_SCALE = 5.0

# Security headers
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

# Django Jet Reboot Configuration
JET_DEFAULT_THEME = 'default'
JET_SIDE_MENU_COMPACT = True
JET_CHANGE_FORM_SIBLING_LINKS = False
JET_CUSTOM_CSS = 'admin/custom_admin.css'

JET_THEMES = [
    {'theme': 'default', 'color': '#1e3a5f', 'title': 'Indigo (Default)'},
    {'theme': 'green', 'color': '#5cb85c', 'title': 'Green'},
    {'theme': 'light-green', 'color': '#8bc34a', 'title': 'Light Green'},
    {'theme': 'light-blue', 'color': '#5dade2', 'title': 'Light Blue'},
    {'theme': 'light-gray', 'color': '#95a5a6', 'title': 'Light Gray'},
    {'theme': 'light-violet', 'color': '#9b59b6', 'title': 'Light Violet'},
]

JET_SIDE_MENU_ITEMS = [
    {'label': 'Dashboard', 'items': [
        {'label': 'Home', 'url': '/admin/', 'url_blank': False},
        {'label': 'Main Dashboard', 'url': '/dashboard/', 'url_blank': False},
    ]},
    {'label': 'Academics', 'items': [
        {'label': 'Courses', 'url': '/admin/academics/course/', 'url_blank': False},
        {'label': 'Departments', 'url': '/admin/academics/department/', 'url_blank': False},
        {'label': 'Course Allocations', 'url': '/admin/academics/courseallocation/', 'url_blank': False},
        {'label': 'Results', 'url': '/admin/academics/result/', 'url_blank': False},
        {'label': 'Attendance', 'url': '/admin/academics/attendance/', 'url_blank': False},
        {'label': 'Timetable', 'url': '/admin/academics/timetable/', 'url_blank': False},
    ]},
    {'label': 'Students', 'items': [
        {'label': 'Students', 'url': '/admin/students/student/', 'url_blank': False},
        {'label': 'Admissions', 'url': '/admin/students/admission/', 'url_blank': False},
        {'label': 'Course Registrations', 'url': '/admin/students/courseregistration/', 'url_blank': False},
    ]},
    {'label': 'Staff', 'items': [
        {'label': 'Staff Members', 'url': '/admin/staff/staff/', 'url_blank': False},
        {'label': 'Departments', 'url': '/admin/staff/department/', 'url_blank': False},
    ]},
    {'label': 'Finance', 'items': [
        {'label': 'Invoices', 'url': '/admin/finance/invoice/', 'url_blank': False},
        {'label': 'Payments', 'url': '/admin/finance/payment/', 'url_blank': False},
        {'label': 'Fee Structure', 'url': '/admin/finance/feestructure/', 'url_blank': False},
    ]},
    {'label': 'Library', 'items': [
        {'label': 'Books', 'url': '/admin/library/book/', 'url_blank': False},
        {'label': 'Categories', 'url': '/admin/library/category/', 'url_blank': False},
        {'label': 'Borrowings', 'url': '/admin/library/borrowing/', 'url_blank': False},
        {'label': 'Fines', 'url': '/admin/library/fine/', 'url_blank': False},
    ]},
    {'label': 'Hostel', 'items': [
        {'label': 'Hostels', 'url': '/admin/hostel/hostel/', 'url_blank': False},
        {'label': 'Rooms', 'url': '/admin/hostel/room/', 'url_blank': False},
        {'label': 'Allocations', 'url': '/admin/hostel/roomallocation/', 'url_blank': False},
        {'label': 'Maintenance', 'url': '/admin/hostel/maintenance/', 'url_blank': False},
    ]},
    {'label': 'Communications', 'items': [
        {'label': 'Announcements', 'url': '/admin/communications/announcement/', 'url_blank': False},
        {'label': 'Messages', 'url': '/admin/communications/message/', 'url_blank': False},
        {'label': 'Notifications', 'url': '/admin/communications/notification/', 'url_blank': False},
    ]},
    {'label': 'System', 'items': [
        {'label': 'Users', 'url': '/admin/accounts/user/', 'url_blank': False},
        {'label': 'Groups', 'url': '/admin/auth/group/', 'url_blank': False},
    ]},
]
