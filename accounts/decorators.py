from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def role_required(allowed_roles):
    """Decorator to restrict view access to specific roles."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if request.user.role in allowed_roles:
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
