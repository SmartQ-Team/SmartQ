from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.db.models import Avg, Count, Max
from django.db.models.functions import TruncHour
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status as http
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from accounts.audit import log_action
from accounts.models import Notification, Profile
from services.models import Department, Service
from .models import QueueEntry
from .serializers import QueueEntrySerializer
from . import queue_logic

NO_STORE = {'Cache-Control': 'no-store'}
STAFF_ROLES = ['STAFF', 'SUPERVISOR', 'ADMIN']


# ------------------------------------------------------------------
# AUTH
# ------------------------------------------------------------------
@ensure_csrf_cookie
@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_bootstrap(request):
    """React calls this once on load to receive the csrftoken cookie."""
    return Response({'ok': True}, headers=NO_STORE)

@ensure_csrf_cookie
@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response({'detail': 'Invalid credentials'}, status=http.HTTP_401_UNAUTHORIZED)
    login(request, user)
    return Response(_me_payload(user))


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    logout(request)
    return Response({'ok': True})




def _me_payload(user):
    profile = getattr(user, 'profile', None)
    return {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'role': profile.role if profile else 'STUDENT',
        'department_id': profile.department_id if profile else None,
        'department_name': profile.department.name if profile and profile.department else None,
        'student_number': profile.student_number if profile else None,
        'is_staff_role': bool(profile and profile.role in STAFF_ROLES),
        'unread_notifications': Notification.objects.filter(user=user, read=False).count(),
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_me(request):
    return Response(_me_payload(request.user))


# ------------------------------------------------------------------
# STUDENT
# ------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_services(request):
    services = Service.objects.filter(active=True).select_related('department')
    out = []
    for s in services:
        waiting = queue_logic.waiting_list(s).count()
        out.append({
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'department_id': s.department.id,
            'department_name': s.department.name,
            'department_location': s.department.location,
            'average_service_time_minutes': s.average_service_time_minutes,
            'waiting': waiting,
            'estimate': queue_logic.estimate_waiting_time(s, waiting),
            'congestion': queue_logic.congestion_status(s),
        })
    return Response(out, headers=NO_STORE)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_departments(request):
    deps = Department.objects.filter(active=True).annotate(service_count=Count('services'))
    return Response([{
        'id': d.id,
        'name': d.name,
        'location': d.location,
        'description': d.description,
        'service_count': d.service_count,
    } for d in deps], headers=NO_STORE)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_my_queue(request):
    entry = QueueEntry.objects.filter(
        student=request.user,
        status__in=queue_logic.ACTIVE_STATUSES,
    ).select_related('service', 'service__department', 'counter').order_by('-join_time').first()

    if not entry:
        return Response({'entry': None})

    ahead = queue_logic.students_ahead(entry)
    estimate = queue_logic.estimate_waiting_time(entry.service, ahead)
    now_serving = queue_logic.active_calls(entry.service).first()

    return Response({
        'entry': QueueEntrySerializer(entry).data,
        'ahead': ahead,
        'estimate': estimate,
        'currently_serving': now_serving.queue_number if now_serving else None,
        'active': entry.status in queue_logic.ACTIVE_STATUSES,
    }, headers=NO_STORE)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_join_queue(request, service_id):
    service = get_object_or_404(Service, id=service_id, active=True)

    existing = QueueEntry.objects.filter(
        student=request.user, status__in=queue_logic.ACTIVE_STATUSES,
    ).exists()
    if existing:
        return Response({'detail': 'You already have an active queue entry.'},
                        status=http.HTTP_400_BAD_REQUEST)

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

    return Response({
        'entry': QueueEntrySerializer(entry).data,
        'message': f'You joined the queue. Your number is {entry.queue_number}.',
    }, status=http.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_cancel_queue(request, entry_id):
    entry = get_object_or_404(QueueEntry, id=entry_id, student=request.user)
    if entry.status not in ['WAITING', 'CALLED']:
        return Response({'detail': 'This queue entry can no longer be cancelled.'},
                        status=http.HTTP_400_BAD_REQUEST)

    entry.status = 'CANCELLED'
    entry.save()
    queue_logic.notify(request.user,
                       f'Your queue entry {entry.queue_number} for {entry.service.name} was cancelled.')
    queue_logic.notify_department_staff(
        entry.service.department, f'{entry.queue_number} cancelled {entry.service.name}.')
    log_action(request, action='QUEUE_CANCEL', entity_type='QueueEntry', entity_id=entry.id,
               details=f'{entry.queue_number} cancelled {entry.service.name}.')

    return Response({'ok': True, 'message': 'Your queue entry was cancelled.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_mark_late(request, entry_id):
    entry = get_object_or_404(QueueEntry, id=entry_id, student=request.user)
    if entry.status != 'WAITING' or entry.running_late:
        return Response({'detail': 'Cannot mark late in current state.'},
                        status=http.HTTP_400_BAD_REQUEST)

    entry.running_late = True
    entry.save()
    queue_logic.notify_late(entry)
    log_action(request, action='MARK_LATE', entity_type='QueueEntry', entity_id=entry.id,
               details=f'{entry.queue_number} reported running late.')

    return Response({'ok': True, 'message': 'Staff have been informed that you are running late.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_queue_status(request, entry_id):
    entry = get_object_or_404(QueueEntry, id=entry_id, student=request.user)
    ahead = queue_logic.students_ahead(entry)
    estimate = queue_logic.estimate_waiting_time(entry.service, ahead)
    now_serving = queue_logic.active_calls(entry.service).first()

    return Response({
        'queue_number': entry.queue_number,
        'status': entry.status,
        'status_display': entry.get_status_display(),
        'ahead': ahead,
        'estimate': estimate,
        'currently_serving': now_serving.queue_number if now_serving else None,
        'running_late': entry.running_late,
        'active': entry.status in queue_logic.ACTIVE_STATUSES,
    }, headers=NO_STORE)


# ------------------------------------------------------------------
# NOTIFICATIONS
# ------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_notifications(request):
    items = Notification.objects.filter(user=request.user).order_by('-created_at')[:60]
    return Response([{
        'id': n.id,
        'message': n.message,
        'created_at': n.created_at.isoformat(),
        'read': n.read,
    } for n in items], headers=NO_STORE)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_notifications_poll(request):
    unread = Notification.objects.filter(user=request.user, read=False).order_by('-created_at')
    return Response({
        'unread': unread.count(),
        'latest': [{
            'id': n.id,
            'message': n.message,
            'created_at': n.created_at.strftime('%H:%M'),
        } for n in unread[:5]],
    }, headers=NO_STORE)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_notifications_read_all(request):
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return Response({'ok': True})


# ------------------------------------------------------------------
# PUBLIC BOARD
# ------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def api_board(request):
    boards = []
    for service in Service.objects.filter(active=True).select_related('department'):
        called = queue_logic.active_calls(service).first()
        boards.append({
            'service_id': service.id,
            'service': service.name,
            'department': service.department.name,
            'now_serving': called.queue_number if called else None,
            'counter': called.counter.name if called and called.counter else None,
            'waiting': queue_logic.waiting_list(service).count(),
        })
    return Response({'boards': boards}, headers=NO_STORE)


# ------------------------------------------------------------------
# STAFF
# ------------------------------------------------------------------
def _scoped_services(user):
    profile = getattr(user, 'profile', None)
    dep = profile.department if profile else None
    qs = Service.objects.filter(active=True).select_related('department')
    return qs.filter(department=dep) if dep else qs


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_staff_dashboard(request):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in STAFF_ROLES:
        return Response({'detail': 'Forbidden'}, status=http.HTTP_403_FORBIDDEN)

    services = _scoped_services(request.user)
    cards = []
    for s in services:
        cards.append({
            'id': s.id,
            'name': s.name,
            'department_name': s.department.name,
            'waiting': queue_logic.waiting_list(s).count(),
            'active_calls': queue_logic.active_calls(s).count(),
            'counters': s.department.counters.filter(active=True).count(),
            'congestion': queue_logic.congestion_status(s),
        })

    today = timezone.localtime(timezone.now()).date()
    entries_today = QueueEntry.objects.filter(service__in=services, join_time__date=today)
    served = entries_today.filter(status='COMPLETED')
    avg = served.aggregate(value=Avg('waiting_time_minutes'))['value']

    return Response({
        'department': profile.department.name if profile.department else None,
        'stats': {
            'waiting_total': sum(c['waiting'] for c in cards),
            'served': served.count(),
            'no_shows': entries_today.filter(status='NO_SHOW').count(),
            'cancelled': entries_today.filter(status='CANCELLED').count(),
            'avg_wait': round(avg) if avg else 0,
        },
        'cards': cards,
    }, headers=NO_STORE)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_staff_queue(request, service_id):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in STAFF_ROLES:
        return Response({'detail': 'Forbidden'}, status=http.HTTP_403_FORBIDDEN)

    service = get_object_or_404(Service, id=service_id)
    waiting_qs = queue_logic.waiting_list(service)
    active_qs = queue_logic.active_calls(service)

    return Response({
        'service': {
            'id': service.id,
            'name': service.name,
            'department_name': service.department.name,
            'counters': service.department.counters.filter(active=True).count(),
        },
        'waiting': [{
            'id': e.id,
            'queue_number': e.queue_number,
            'position': e.position,
            'student': e.student.username,
            'running_late': e.running_late,
        } for e in waiting_qs],
        'active': [{
            'id': e.id,
            'queue_number': e.queue_number,
            'status': e.status,
            'status_display': e.get_status_display(),
            'counter': e.counter.name if e.counter else None,
        } for e in active_qs],
    }, headers=NO_STORE)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_call_next(request, service_id):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in STAFF_ROLES:
        return Response({'detail': 'Forbidden'}, status=http.HTTP_403_FORBIDDEN)

    service = get_object_or_404(Service, id=service_id)

    with transaction.atomic():
        active_count = queue_logic.active_calls(service).count()
        counter_count = service.department.counters.filter(active=True).count() or 1
        if active_count >= counter_count:
            return Response({'detail': 'All counters are busy.'}, status=http.HTTP_400_BAD_REQUEST)

        entry = queue_logic.waiting_list(service).select_for_update().first()
        if not entry:
            return Response({'detail': 'No students waiting.'}, status=http.HTTP_400_BAD_REQUEST)

        busy_ids = list(queue_logic.active_calls(service).values_list('counter_id', flat=True))
        free_counter = service.department.counters.filter(active=True).exclude(id__in=busy_ids).first()

        entry.status = 'CALLED'
        entry.called_time = timezone.now()
        if free_counter:
            entry.counter = free_counter
        entry.save()

        queue_logic.notify_called(entry)
        queue_logic.notify_turn_approaching(service)
        queue_logic.email_student_called(entry, request)

    log_action(request, action='CALL_NEXT', entity_type='QueueEntry', entity_id=entry.id,
               details=f'{request.user.username} called {entry.queue_number} for {service.name}.')

    return Response({'ok': True, 'called': QueueEntrySerializer(entry).data,
                     'message': f'Called {entry.queue_number}.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_mark_arrived(request, entry_id):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in STAFF_ROLES:
        return Response({'detail': 'Forbidden'}, status=http.HTTP_403_FORBIDDEN)

    entry = get_object_or_404(QueueEntry, id=entry_id)
    if entry.status != 'CALLED':
        return Response({'detail': 'Entry is not in CALLED state.'}, status=http.HTTP_400_BAD_REQUEST)

    entry.status = 'ARRIVED'
    entry.arrival_time = timezone.now()
    entry.save()
    log_action(request, action='MARK_ARRIVED', entity_type='QueueEntry', entity_id=entry.id,
               details=f'{entry.queue_number} marked arrived.')
    return Response({'ok': True, 'entry': QueueEntrySerializer(entry).data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_mark_served(request, entry_id):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in STAFF_ROLES:
        return Response({'detail': 'Forbidden'}, status=http.HTTP_403_FORBIDDEN)

    entry = get_object_or_404(QueueEntry, id=entry_id)
    if entry.status not in ['CALLED', 'ARRIVED', 'SERVING']:
        return Response({'detail': 'Entry cannot be served from current state.'},
                        status=http.HTTP_400_BAD_REQUEST)

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
    return Response({'ok': True, 'entry': QueueEntrySerializer(entry).data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_mark_no_show(request, entry_id):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in STAFF_ROLES:
        return Response({'detail': 'Forbidden'}, status=http.HTTP_403_FORBIDDEN)

    entry = get_object_or_404(QueueEntry, id=entry_id)
    if entry.status not in ['CALLED', 'ARRIVED']:
        return Response({'detail': 'Entry cannot be marked no-show from current state.'},
                        status=http.HTTP_400_BAD_REQUEST)

    entry.status = 'NO_SHOW'
    entry.save()
    queue_logic.notify_no_show(entry)
    queue_logic.notify_turn_approaching(entry.service)
    log_action(request, action='MARK_NO_SHOW', entity_type='QueueEntry', entity_id=entry.id,
               details=f'{entry.queue_number} marked as no-show.')
    return Response({'ok': True, 'entry': QueueEntrySerializer(entry).data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_reschedule(request, entry_id):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in STAFF_ROLES:
        return Response({'detail': 'Forbidden'}, status=http.HTTP_403_FORBIDDEN)

    entry = get_object_or_404(QueueEntry, id=entry_id)
    if entry.status != 'WAITING':
        return Response({'detail': 'Only WAITING entries can be rescheduled.'},
                        status=http.HTTP_400_BAD_REQUEST)

    target_id = request.data.get('target_id')
    with transaction.atomic():
        if target_id:
            target = get_object_or_404(QueueEntry, id=int(target_id), service=entry.service)
            entry.join_time = target.join_time + timezone.timedelta(seconds=1)
        else:
            entry.join_time = timezone.now() + timezone.timedelta(seconds=1)
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

    return Response({'ok': True, 'message': f'{entry.queue_number} rescheduled.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_analytics(request):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in STAFF_ROLES:
        return Response({'detail': 'Forbidden'}, status=http.HTTP_403_FORBIDDEN)

    services = _scoped_services(request.user)
    today = timezone.localtime(timezone.now()).date()
    entries = QueueEntry.objects.filter(service__in=services, join_time__date=today)
    served = entries.filter(status='COMPLETED')

    avg_wait = served.aggregate(v=Avg('waiting_time_minutes'))['v']
    avg_service = served.aggregate(v=Avg('service_duration_minutes'))['v']
    max_queue = entries.aggregate(v=Max('position'))['v']

    peak = list(
        entries.annotate(hour=TruncHour('join_time'))
               .values('hour').annotate(count=Count('id')).order_by('hour')
    )

    counters = []
    if profile.department:
        for c in profile.department.counters.filter(active=True):
            counters.append({'counter': c.name, 'served': served.filter(counter=c).count()})

    return Response({
        'department': profile.department.name if profile.department else 'All departments',
        'summary': {
            'served': served.count(),
            'no_shows': entries.filter(status='NO_SHOW').count(),
            'cancelled': entries.filter(status='CANCELLED').count(),
            'waiting_now': QueueEntry.objects.filter(service__in=services, status='WAITING').count(),
            'avg_wait': round(avg_wait) if avg_wait else 0,
            'avg_service': round(avg_service) if avg_service else 0,
            'max_queue': max_queue or 0,
        },
        'peak_periods': [{
            'hour': p['hour'].strftime('%H:%M') if p['hour'] else '--:--',
            'count': p['count'],
        } for p in peak],
        'counters': counters,
    }, headers=NO_STORE)


# ------------------------------------------------------------------
# REPORT ISSUE (JSON variant)
# ------------------------------------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_report_issue(request):
    from django.conf import settings
    from django.template.loader import render_to_string
    from smartq.mailer import send_email

    category = request.data.get('category', 'Bug')
    description = (request.data.get('description') or '').strip()
    if not description:
        return Response({'detail': 'Please describe the problem.'},
                        status=http.HTTP_400_BAD_REQUEST)

    subject = f'SmartQ report ({category}) from {request.user.username}'
    body = (
        f'User: {request.user.username} ({request.user.email})\n'
        f'Category: {category}\n'
        f'Time: {timezone.now()}\n\n{description}\n'
    )
    html = render_to_string('emails/report_issue.html', {
        'category': category,
        'description': description,
        'username': request.user.username,
        'user_email': request.user.email,
        'reported_at': timezone.now().strftime('%d %b %Y, %H:%M'),
        'button_url': request.build_absolute_uri('/admin/'),
    })
    delivered = send_email(subject, body, [settings.ADMIN_REPORT_EMAIL], html=html)

    log_action(request, action='REPORT_ISSUE', entity_type='Report', entity_id=None,
               details=f'{category}: {description[:100]}')

    return Response({
        'ok': True,
        'delivered': delivered,
        'message': ('Your report was emailed to the administrator. Thank you!'
                    if delivered else
                    'Report saved to the audit log, but email could not be sent.'),
    })
