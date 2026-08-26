from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

STAFF_ROLES = ['STAFF', 'SUPERVISOR', 'ADMIN']


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        profile = getattr(request.user, 'profile', None)
        if profile is None or profile.role not in STAFF_ROLES:
            messages.error(request, 'You do not have permission to access the staff area.')
            return redirect('home')

        return view_func(request, *args, **kwargs)

    return wrapper