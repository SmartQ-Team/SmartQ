from .models import AuditLog


def get_client_ip(request):
    if request is None:
        return None
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_action(request=None, user=None, action='', entity_type='', entity_id=None, details=''):
    """Write an immutable audit row.

    Handles both Django and DRF request objects, and gracefully tolerates
    `request.user is None` (which happens when REST_FRAMEWORK uses
    UNAUTHENTICATED_USER = None).
    """
    # Normalize: if a user was passed but is AnonymousUser, treat as None
    if user is not None and not getattr(user, 'is_authenticated', False):
        user = None

    # If no user was passed, try to pull from the request — but safely
    if user is None and request is not None:
        req_user = getattr(request, 'user', None)
        if req_user is not None and getattr(req_user, 'is_authenticated', False):
            user = req_user

    AuditLog.objects.create(
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=get_client_ip(request),
    )