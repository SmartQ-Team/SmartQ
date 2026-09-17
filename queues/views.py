from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count, Max
from django.db.models.functions import TruncHour
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from accounts.audit import log_action
from accounts.decorators import staff_required
from services.models import Department, Service
from .models import QueueEntry
from . import queue_logic

NO_STORE = {'Cache-Control': 'no-store'}


@login_required
def student_dashboard(request):
    active_entry = QueueEntry.objects.filter(
        student=request.user, status__in=queue_logic.ACTIVE_STATUSES,
    ).order_by('-join_time').first()

    services_list = []
    for service in Service.objects.filter(active=True).select_related('department'):
        waiting = queue_logic.get_active_entries(service).count()
        services_list.append({
            'service': service,
            'waiting': waiting,
            'estimate': queue_logic.estimate_waiting_time(service, waiting),
            'congestion': queue_logic.congestion_status(service),
        })

    departments = Department.objects.filter(active=True).annotate(service_count=Count('services'))

    context = {
        'services_list': services_list,
        'active_entry': active_entry,
        'departments': departments,
    }
    return render(request, 'queues/student_dashboard.html', context)


@login_required
def join_queue(request, service_id):
    service = get_object_or_404(Service, id=service_id, active=True)

    if request.method == 'POST':
        existing = QueueEntry.objects.filter(
            student=request.user, status__in=queue_logic.ACTIVE_STATUSES,
        ).exists()
        if existing:
            messages.error(request, 'You already have an active queue entry.')
            return redirect('student_dashboard')

        with transaction.atomic():
            position = queue_logic.get_active_entries(service).count() + 1
            counters_now = service.department.counters.filter(active=True).count() or 1
            entry = QueueEntry.objects.create(
                service=service,
                student=request.user,
                queue_number=queue_logic.generate_queue_number(service),
                status='WAITING',
                position=position,
                counters_at_join=counters_now,
            )

        queue_logic.notify_department_staff(
            service.department, f'{entry.queue_number} joined {service.name}.'
        )
        log_action(request, action='QUEUE_JOIN', entity_type='QueueEntry', entity_id=entry.id,
                   details=f'{entry.queue_number} joined {service.name}.')
        messages.success(request, f'You joined the queue. Your number is {entry.queue_number}.')
        return redirect('my_queue')

    return redirect('student_dashboard')


@login_required
def my_queue(request):
    entry = QueueEntry.objects.filter(
        student=request.user,
        status__in=queue_logic.ACTIVE_STATUSES,
    ).order_by('-join_time').first()

    if not entry:
        messages.info(request, 'You have no active queue entry.')
        return redirect('student_dashboard')

    ahead = queue_logic.students_ahead(entry)
    context = {
        'entry': entry,
        'ahead': ahead,
        'estimate': queue_logic.estimate_waiting_time(entry.service, ahead),
        'currently_serving': queue_logic.active_calls(entry.service).first(),
    }
    return render(request, 'queues/my_queue.html', context)


@login_required
def cancel_queue(request, entry_id):
    entry = get_object_or_404(QueueEntry, id=entry_id, student=request.user)

    if entry.status in ['WAITING', 'CALLED']:
        entry.status = 'CANCELLED'
        entry.save()
        queue_logic.notify(request.user, f'Your queue entry {entry.queue_number} for {entry.service.name} was cancelled.')
        queue_logic.notify_department_staff(
            entry.service.department, f'{entry.queue_number} cancelled {entry.service.name}.'
        )
        log_action(request, action='QUEUE_CANCEL', entity_type='QueueEntry', entity_id=entry.id,
                   details=f'{entry.queue_number} cancelled {entry.service.name}.')
        messages.success(request, 'Your queue entry was cancelled.')
    else:
        messages.error(request, 'This queue entry can no longer be cancelled.')

    return redirect('student_dashboard')


@login_required
def mark_late(request, entry_id):
    """Item 9: student informs staff they will run late."""
    entry = get_object_or_404(QueueEntry, id=entry_id, student=request.user)

    if request.method == 'POST' and entry.status == 'WAITING' and not entry.running_late:
        entry.running_late = True
        entry.save()
        queue_logic.notify_late(entry)
        log_action(request, action='MARK_LATE', entity_type='QueueEntry', entity_id=entry.id,
                   details=f'{entry.queue_number} reported running late.')
        messages.info(request, 'Staff have been informed that you are running late.')

    return redirect('my_queue')


@staff_required
def reschedule_entry(request, entry_id):
    """Item 9: staff move a late student after a chosen queue number (or to the end)."""
    entry = get_object_or_404(QueueEntry, id=entry_id)

    if request.method == 'POST' and entry.status == 'WAITING':
        target_id = request.POST.get('target_id')
        with transaction.atomic():
            if target_id:
                target = get_object_or_404(QueueEntry, id=int(target_id), service=entry.service)
                entry.join_time = target.join_time + timedelta(seconds=1)
            else:
                entry.join_time = timezone.now() + timedelta(seconds=1)
            entry.running_late = False
            entry.save()
            queue_logic.recalculate_positions(entry.service)

        ahead = queue_logic.students_ahead(entry)
        queue_logic.notify(
            entry.student,
            f'Your queue number {entry.queue_number} was rescheduled. Students now ahead of you: {ahead}.',
        )
        log_action(request, action='RESCHEDULE', entity_type='QueueEntry', entity_id=entry.id,
                   details=f'{entry.queue_number} rescheduled by {request.user.username}; ahead={ahead}.')
        messages.success(request, f'{entry.queue_number} rescheduled.')

    return redirect('staff_queue', service_id=entry.service.id)


@staff_required
def staff_dashboard(request):
    profile = getattr(request.user, 'profile', None)
    department = profile.department if profile else None

    services = Service.objects.filter(department=department, active=True) if department else Service.objects.filter(active=True)
    services = services.select_related('department')

    service_cards = []
    for service in services:
        service_cards.append({
            'service': service,
            'waiting': queue_logic.waiting_list(service).count(),
            'active_calls': queue_logic.active_calls(service).count(),
            'counters': service.department.counters.filter(active=True).count(),
            'congestion': queue_logic.congestion_status(service),
        })

    today = timezone.localtime(timezone.now()).date()
    entries_today = QueueEntry.objects.filter(service__in=services, join_time__date=today)
    served = entries_today.filter(status='COMPLETED')
    average = served.aggregate(value=Avg('waiting_time_minutes'))['value']

    stats = {
        'waiting_total': sum(card['waiting'] for card in service_cards),
        'served': served.count(),
        'no_shows': entries_today.filter(status='NO_SHOW').count(),
        'cancelled': entries_today.filter(status='CANCELLED').count(),
        'avg_wait': round(average) if average else 0,
    }

    context = {'department': department, 'service_cards': service_cards, 'stats': stats}
    return render(request, 'queues/staff_dashboard.html', context)


@staff_required
def staff_dashboard_api(request):
    """Item 6: live JSON feed for the staff dashboard."""
    profile = getattr(request.user, 'profile', None)
    department = profile.department if profile else None
    services = Service.objects.filter(department=department, active=True) if department else Service.objects.filter(active=True)

    cards = [{
        'id': s.id,
        'waiting': queue_logic.waiting_list(s).count(),
        'active_calls': queue_logic.active_calls(s).count(),
    } for s in services]

    today = timezone.localtime(timezone.now()).date()
    entries_today = QueueEntry.objects.filter(service__in=services, join_time__date=today)
    served = entries_today.filter(status='COMPLETED')
    average = served.aggregate(value=Avg('waiting_time_minutes'))['value']

    payload = {
        'stats': {
            'waiting_total': sum(c['waiting'] for c in cards),
            'served': served.count(),
            'no_shows': entries_today.filter(status='NO_SHOW').count(),
            'cancelled': entries_today.filter(status='CANCELLED').count(),
            'avg_wait': round(average) if average else 0,
        },
        'cards': cards,
    }
    return JsonResponse(payload, headers=NO_STORE)


@staff_required
def staff_queue(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    context = {
        'service': service,
        'waiting': queue_logic.waiting_list(service),
        'active': queue_logic.active_calls(service),
        'active_count': queue_logic.active_calls(service).count(),
        'counter_count': service.department.counters.filter(active=True).count(),
    }
    return render(request, 'queues/staff_queue.html', context)


@staff_required
def staff_queue_api(request, service_id):
    """Items 6/7/9/15: live JSON feed for queue management."""
    service = get_object_or_404(Service, id=service_id)
    payload = {
        'waiting': [{
            'id': e.id,
            'queue_number': e.queue_number,
            'position': e.position,
            'student': e.student.username,
            'running_late': e.running_late,
        } for e in queue_logic.waiting_list(service)],
        'active': [{
            'id': e.id,
            'queue_number': e.queue_number,
            'status': e.status,
            'status_display': e.get_status_display(),
            'counter': e.counter.name if e.counter else None,
        } for e in queue_logic.active_calls(service)],
    }
    return JsonResponse(payload, headers=NO_STORE)


@staff_required
def call_next(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        with transaction.atomic():
            active_count = queue_logic.active_calls(service).count()
            counter_count = service.department.counters.filter(active=True).count() or 1

            if active_count >= counter_count:
                messages.error(request, 'All counters are busy. Complete or no-show a student first.')
                return redirect('staff_queue', service_id=service.id)

            entry = queue_logic.waiting_list(service).select_for_update().first()
            if not entry:
                messages.info(request, 'No students waiting.')
                return redirect('staff_queue', service_id=service.id)

            busy_ids = list(queue_logic.active_calls(service).values_list('counter_id', flat=True))
            free_counter = (
                service.department.counters.filter(active=True).exclude(id__in=busy_ids).first()
            )

            entry.status = 'CALLED'
            entry.called_time = timezone.now()
            if free_counter:
                entry.counter = free_counter
            entry.save()
            queue_logic.notify_called(entry)
            queue_logic.notify_turn_approaching(service)
            queue_logic.email_student_called(entry)   # Item 3

        log_action(request, action='CALL_NEXT', entity_type='QueueEntry', entity_id=entry.id,
                   details=f'{request.user.username} called {entry.queue_number} for {service.name}.')
        messages.success(request, f'Called {entry.queue_number}.')

    return redirect('staff_queue', service_id=service.id)


@staff_required
def mark_arrived(request, entry_id):
    entry = get_object_or_404(QueueEntry, id=entry_id)
    if request.method == 'POST' and entry.status == 'CALLED':
        entry.status = 'ARRIVED'
        entry.arrival_time = timezone.now()
        entry.save()
        log_action(request, action='MARK_ARRIVED', entity_type='QueueEntry', entity_id=entry.id,
                   details=f'{entry.queue_number} marked arrived.')
        messages.success(request, f'{entry.queue_number} arrived.')
    return redirect('staff_queue', service_id=entry.service.id)


@staff_required
def mark_served(request, entry_id):
    entry = get_object_or_404(QueueEntry, id=entry_id)
    if request.method == 'POST' and entry.status in ['CALLED', 'ARRIVED', 'SERVING']:
        now = timezone.now()
        entry.status = 'COMPLETED'
        entry.completion_time = now
        if entry.called_time:
            entry.waiting_time_minutes = int((entry.called_time - entry.join_time).total_seconds() // 60)
            entry.service_duration_minutes = int((now - entry.called_time).total_seconds() // 60)
        entry.save()
        queue_logic.notify_completed(entry)
        queue_logic.notify_turn_approaching(entry.service)
        log_action(request, action='MARK_SERVED', entity_type='QueueEntry', entity_id=entry.id,
                   details=f'{entry.queue_number} marked served.')
        messages.success(request, f'{entry.queue_number} marked as served.')
    return redirect('staff_queue', service_id=entry.service.id)


@staff_required
def mark_no_show(request, entry_id):
    entry = get_object_or_404(QueueEntry, id=entry_id)
    if request.method == 'POST' and entry.status in ['CALLED', 'ARRIVED']:
        entry.status = 'NO_SHOW'
        entry.save()
        queue_logic.notify_no_show(entry)
        queue_logic.notify_turn_approaching(entry.service)
        log_action(request, action='MARK_NO_SHOW', entity_type='QueueEntry', entity_id=entry.id,
                   details=f'{entry.queue_number} marked as no-show.')
        messages.warning(request, f'{entry.queue_number} marked as no-show.')
    return redirect('staff_queue', service_id=entry.service.id)


@staff_required
def analytics(request):
    profile = getattr(request.user, 'profile', None)
    department = profile.department if profile else None
    services = Service.objects.filter(department=department, active=True) if department else Service.objects.filter(active=True)

    today = timezone.localtime(timezone.now()).date()
    entries = QueueEntry.objects.filter(service__in=services, join_time__date=today)
    served = entries.filter(status='COMPLETED')

    avg_wait = served.aggregate(value=Avg('waiting_time_minutes'))['value']
    avg_service = served.aggregate(value=Avg('service_duration_minutes'))['value']
    max_queue = entries.aggregate(value=Max('position'))['value']

    summary = {
        'served': served.count(),
        'no_shows': entries.filter(status='NO_SHOW').count(),
        'cancelled': entries.filter(status='CANCELLED').count(),
        'waiting_now': QueueEntry.objects.filter(service__in=services, status='WAITING').count(),
        'avg_wait': round(avg_wait) if avg_wait else 0,
        'avg_service': round(avg_service) if avg_service else 0,
        'max_queue': max_queue or 0,
    }

    peak_periods = (
        entries.annotate(hour=TruncHour('join_time')).values('hour').annotate(count=Count('id')).order_by('hour')
    )
    max_peak = max([p['count'] for p in peak_periods], default=1)

    counters = []
    if department:
        for counter in department.counters.filter(active=True):
            counters.append({'counter': counter, 'served': served.filter(counter=counter).count()})

    context = {
        'department': department, 'summary': summary,
        'peak_periods': peak_periods, 'max_peak': max_peak, 'counters': counters,
    }
    return render(request, 'queues/analytics.html', context)


@login_required
def queue_status_api(request, entry_id):
    entry = get_object_or_404(QueueEntry, id=entry_id, student=request.user)
    ahead = queue_logic.students_ahead(entry)
    estimate = queue_logic.estimate_waiting_time(entry.service, ahead)
    now_serving = queue_logic.active_calls(entry.service).first()

    return JsonResponse({
        'queue_number': entry.queue_number,
        'status': entry.status,
        'status_display': entry.get_status_display(),
        'ahead': ahead,
        'estimate': estimate,
        'currently_serving': now_serving.queue_number if now_serving else None,
        'running_late': entry.running_late,
        'active': entry.status in queue_logic.ACTIVE_STATUSES,
    }, headers=NO_STORE)