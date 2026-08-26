from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .audit import log_action


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    log_action(
        request=request,
        user=user,
        action='LOGIN_SUCCESS',
        details=f'{user.username} logged in.',
    )


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    if user is not None and user.is_authenticated:
        log_action(
            request=request,
            user=user,
            action='LOGOUT',
            details=f'{user.username} logged out.',
        )


@receiver(user_login_failed)
def on_user_login_failed(sender, credentials, request=None, **kwargs):
    username = credentials.get('username', 'unknown')
    log_action(
        request=request,
        user=None,
        action='LOGIN_FAILED',
        details=f'Failed login attempt for username: {username}.',
    )