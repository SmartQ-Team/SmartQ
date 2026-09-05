from django.utils import timezone

from accounts.models import Notification

from .models import QueueEntry

ACTIVE_STATUSES = ['WAITING', 'CALLED', 'ARRIVED', 'SERVING']


def get_active_entries(service):
    return QueueEntry.objects.filter(
        service=service,
        status__in=ACTIVE_STATUSES,
    ).order_by('join_time')


def waiting_list(service):
    return QueueEntry.objects.filter(
        service=service,
        status='WAITING',
    ).order_by('join_time')


def active_calls(service):
    return QueueEntry.objects.filter(
        service=service,
        status__in=['CALLED', 'ARRIVED', 'SERVING'],
    ).order_by('called_time')


def students_ahead(entry):
    return get_active_entries(entry.service).filter(
        join_time__lt=entry.join_time
    ).count()


def estimate_waiting_time(service, ahead):
    ml_estimate = predict_with_ml(service, ahead)
    if ml_estimate is not None:
        return ml_estimate

    average_time = service.average_service_time_minutes or 10
    active_counters = service.department.counters.filter(active=True).count() or 1
    return round((ahead * average_time) / active_counters)


def predict_with_ml(service, ahead):
    try:
        from . import ml_model
    except ImportError:
        return None
    return ml_model.predict_waiting_time(service, ahead)


def congestion_status(service):
    waiting = waiting_list(service).count()
    estimate = estimate_waiting_time(service, waiting)

    if waiting > 25 or estimate > 45:
        return {'label': 'Congested', 'css': 'danger'}
    if waiting >= 10 or estimate >= 15:
        return {'label': 'Moderate', 'css': 'warning'}
    return {'label': 'Normal', 'css': 'success'}


def generate_queue_number(service):
    prefix = service.department.name[:3].upper().replace(' ', '')
    today = timezone.localtime(timezone.now()).date()

    count = QueueEntry.objects.filter(
        service=service,
        join_time__date=today,
    ).count() + 1

    return f"{prefix}-A{count:03d}"


def notify(user, message):
    Notification.objects.create(user=user, message=message)


def notify_called(entry):
    notify(entry.student, f'Your number {entry.queue_number} has been called for {entry.service.name}.')


def notify_completed(entry):
    notify(entry.student, f'Your number {entry.queue_number} has been served. Thank you.')


def notify_no_show(entry):
    notify(entry.student, f'Your number {entry.queue_number} was marked as a no-show.')


def notify_turn_approaching(service):
    for entry in waiting_list(service):
        if students_ahead(entry) <= 2:
            message = f'Your turn is approaching for {entry.service.name} ({entry.queue_number}).'
            already = Notification.objects.filter(
                user=entry.student,
                message=message,
                read=False,
            ).exists()
            if not already:
                notify(entry.student, message)