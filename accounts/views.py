from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from accounts.audit import log_action
from accounts.forms import StudentRegistrationForm
from accounts.models import Notification

NO_STORE = {'Cache-Control': 'no-store'}


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role in ['STAFF', 'SUPERVISOR', 'ADMIN']:
        return redirect('staff_dashboard')
    return redirect('student_dashboard')


def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            log_action(request, action='REGISTER', entity_type='User', entity_id=user.id,
                       details=f'Student {user.username} registered.')
            messages.success(request, 'Welcome to SmartQ!')
            return redirect('student_dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def notifications(request):
    items = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/notifications.html', {'notifications': items})


@login_required
def notifications_read_all(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, read=False).update(read=True)
    return redirect('notifications')


@login_required
def notifications_api(request):
    """Item 8: live bell + banner feed for EVERY page, students AND staff."""
    unread = Notification.objects.filter(user=request.user, read=False).order_by('-created_at')
    payload = {
        'unread': unread.count(),
        'latest': [{
            'id': n.id,
            'message': n.message,
            'created_at': n.created_at.strftime('%H:%M'),
        } for n in unread[:5]],
    }
    return JsonResponse(payload, headers=NO_STORE)


@login_required
def report_issue(request):
    """Item 12: email a problem report to the administrator."""
    if request.method == 'POST':
        category = request.POST.get('category', 'Bug')
        description = request.POST.get('description', '').strip()
        if not description:
            messages.error(request, 'Please describe the problem.')
            return redirect('report_issue')

        subject = f'SmartQ report ({category}) from {request.user.username}'
        body = (
            f'User: {request.user.username} ({request.user.email})\n'
            f'Category: {category}\n'
            f'Time: {timezone.now()}\n\n'
            f'{description}\n'
        )
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_REPORT_EMAIL], fail_silently=True)
        log_action(request, action='REPORT_ISSUE', entity_type='Report', entity_id=None,
                   details=f'{category}: {description[:100]}')
        messages.success(request, 'Your report was emailed to the administrator. Thank you!')
        return redirect('home')

    return render(request, 'accounts/report.html')