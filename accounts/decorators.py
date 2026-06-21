from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.conf import settings


def role_required(allowed_roles):
    """Decorator to restrict view access to specific roles."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # If the user is not authenticated, redirect to the login page
            if not request.user.is_authenticated:
                login_url = getattr(settings, 'LOGIN_URL', '/accounts/login/')
                return redirect(f"{login_url}?next={request.path}")

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if getattr(request.user, 'role', None) in allowed_roles:
                return view_func(request, *args, **kwargs)

            messages.error(request, 'You do not have permission to access this page.')
            raise PermissionDenied
        return wrapper
    return decorator


def admin_required(view_func):
    """Only allow admin users."""
    return role_required(['admin'])(view_func)


def staff_required(view_func):
    """Allow admin, registrar, lecturer, finance staff."""
    return role_required(['admin', 'registrar', 'lecturer', 'finance'])(view_func)


def finance_required(view_func):
    """Only allow finance and admin users."""
    return role_required(['admin', 'finance'])(view_func)


def registrar_required(view_func):
    """Only allow registrar and admin users."""
    return role_required(['admin', 'registrar'])(view_func)


def faculty_dean_required(view_func):
    """Only allow faculty dean or admin users."""
    return role_required(['admin', 'faculty_dean'])(view_func)


def department_head_required(view_func):
    """Only allow department head or admin users."""
    return role_required(['admin', 'department_head'])(view_func)


def programme_coordinator_required(view_func):
    """Only allow programme coordinator or admin users."""
    return role_required(['admin', 'programme_coordinator'])(view_func)


def academic_required(view_func):
    """Allow admin, registrar, faculty dean, department head, and programme coordinator."""
    return role_required(['admin', 'registrar', 'faculty_dean', 'department_head', 'programme_coordinator'])(view_func)


def academic_read_required(view_func):
    """Allow reading academic data: admin, registrar, faculty dean, department head, programme coordinator, lecturer, student."""
    return role_required(['admin', 'registrar', 'faculty_dean', 'department_head', 'programme_coordinator', 'lecturer', 'student'])(view_func)
