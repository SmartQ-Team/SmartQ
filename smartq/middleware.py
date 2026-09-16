import time

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect

API_PREFIXES = ('/queue/api/', '/staff/api/', '/notifications/api/')


class IdleRedirectMiddleware:
    """Item 2: return authenticated users to the home page after 30 minutes idle."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            now = time.time()
            last = request.session.get('last_activity')
            limit = getattr(settings, 'IDLE_REDIRECT_SECONDS', 1800)

            if last and (now - last) > limit and request.path != '/':
                request.session['last_activity'] = now
                messages.info(
                    request,
                    'You were returned to the home page after 30 minutes of inactivity.',
                )
                return redirect('home')

            if not request.path.startswith(API_PREFIXES):
                request.session['last_activity'] = now

        return self.get_response(request)