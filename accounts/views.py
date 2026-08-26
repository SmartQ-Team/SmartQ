from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .audit import log_action
from .forms import StudentRegistrationForm
from .models import Notification


def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            log_action(
                request,
                user=user,
                action='REGISTER',
                entity_type='User',
                entity_id=user.id,
                details=f'New student account created: {user.username}.',
            )
            return redirect('home')
    else:
        form = StudentRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile = getattr(request.user, 'profile', None)
    if profile and profile.role in ['STAFF', 'SUPERVISOR', 'ADMIN']:
        return redirect('staff_dashboard')

    return redirect('student_dashboard')


@login_required
def notifications_page(request):
    notifications = request.user.notifications.all()[:50]
    return render(request, 'accounts/notifications.html', {'notifications': notifications})


@login_required
def mark_all_read(request):
    if request.method == 'POST':
        request.user.notifications.filter(read=False).update(read=True)
        messages.success(request, 'All notifications marked as read.')
    return redirect('notifications')