import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def _send_https(subject, body, recipients, html=None):
    import requests

    key = getattr(settings, 'BREVO_API_KEY', '')
    sender = getattr(settings, 'BREVO_SENDER_EMAIL', settings.DEFAULT_FROM_EMAIL)
    if not key:
        logger.warning('BREVO_API_KEY is not set in settings.py.')
        return False

    payload = {
        'sender': {'name': 'SmartQ', 'email': sender},
        'to': [{'email': e} for e in recipients],
        'subject': subject,
        'textContent': body,
    }
    if html:
        payload['htmlContent'] = html

    resp = requests.post(
        'https://api.brevo.com/v3/smtp/email',
        headers={'api-key': key, 'Content-Type': 'application/json'},
        json=payload,
        timeout=8,
    )
    ok = resp.status_code in (200, 201)
    if not ok:
        logger.warning('Brevo responded %s: %s', resp.status_code, resp.text[:300])
    return ok


def _send_smtp(subject, body, recipients, html=None):
    from django.core.mail import EmailMessage, get_connection
    connection = get_connection(timeout=8)
    msg = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, recipients, connection=connection)
    if html:
        msg.attach_alternative(html, 'text/html')
    msg.send()
    return True


def send_email(subject, body, recipients, html=None):
    """HTTPS email API first (works on every network); SMTP as backup."""
    if isinstance(recipients, str):
        recipients = [recipients]
    recipients = [r for r in recipients if r]

    if not recipients:
        logger.warning('No recipient email address on this user - email skipped. Set it in /admin/.')
        return False

    try:
        if _send_https(subject, body, recipients, html=html):
            return True
    except Exception as exc:
        logger.warning('HTTPS email API failed: %s: %s', type(exc).__name__, exc)

    try:
        return _send_smtp(subject, body, recipients, html=html)
    except Exception as exc:
        logger.warning('SMTP fallback failed: %s: %s', type(exc).__name__, exc)

    return False