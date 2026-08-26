from .models import AuditLog


def get_client_ip(request):
    if request is None:
        return None
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_action(request=None, user=None, action='', entity_type='', entity_id=None, details=''):
    if user is not None and not user.is_authenticated:
        user = None

    if user is None and request is not None and request.user.is_authenticated:
        user = request.user

    AuditLog.objects.create(
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=get_client_ip(request),
    )