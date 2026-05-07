"""Audit log middleware — records every authenticated write action."""
import json
from django.utils.deprecation import MiddlewareMixin


class AuditLogMiddleware(MiddlewareMixin):
    WRITE_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}

    def process_response(self, request, response):
        if request.method not in self.WRITE_METHODS:
            return response
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response
        # Only log successful mutations
        if response.status_code not in (200, 201, 204, 302):
            return response
        try:
            from accounts.models import AuditLog
            path = request.path
            details = {}
            if request.method in ('POST', 'PUT', 'PATCH'):
                try:
                    body = request.body
                    if body:
                        details = json.loads(body)
                except Exception:
                    details = {}
            AuditLog.objects.create(
                user=request.user,
                action=f"{request.method} {path}",
                model_name=_extract_model(path),
                object_id=_extract_id(path),
                details={k: v for k, v in details.items() if k not in ('password', 'csrfmiddlewaretoken')},
                ip_address=_get_ip(request),
            )
        except Exception:
            pass
        return response


def _get_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _extract_model(path):
    parts = [p for p in path.strip('/').split('/') if p]
    if len(parts) >= 2:
        return parts[1]
    return ''


def _extract_id(path):
    parts = [p for p in path.strip('/').split('/') if p]
    if len(parts) >= 3:
        return parts[2]
    return ''
