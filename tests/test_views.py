from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from accounts.models import Notification
from queues.models import QueueEntry

pytestmark = pytest.mark.django_db


def test_login_required_redirects(client, service):
    response = client.get(reverse('student_dashboard'))
    assert response.status_code == 302
    assert 'login' in response.url


def test_student_join_queue(student_client, service, student_user):
    response = student_client.post(reverse('join_queue', args=[service.id]))
    assert response.status_code == 302
    entry = QueueEntry.objects.get(student=student_user)
    assert entry.status == 'WAITING'
    assert entry.position == 1


def test_duplicate_join_blocked(student_client, service):
    student_client.post(reverse('join_queue', args=[service.id]))
    response = student_client.post(reverse('join_queue', args=[service.id]), follow=True)
    messages = [str(m) for m in response.context['messages']]
    assert any('already have an active queue' in m for m in messages)


def test_cancel_own_entry(student_client, service, student_user):
    student_client.post(reverse('join_queue', args=[service.id]))
    entry = QueueEntry.objects.get(student=student_user)
    student_client.post(reverse('cancel_queue', args=[entry.id]))
    entry.refresh_from_db()
    assert entry.status == 'CANCELLED'


def test_cannot_cancel_other_students_entry(student_client, service, staff_user):
    other = QueueEntry.objects.create(service=service, student=staff_user, queue_number='X1', position=1)
    response = student_client.post(reverse('cancel_queue', args=[other.id]))
    assert response.status_code == 404


def test_status_api_json(student_client, service, student_user):
    student_client.post(reverse('join_queue', args=[service.id]))
    entry = QueueEntry.objects.get(student=student_user)
    response = student_client.get(reverse('queue_status_api', args=[entry.id]))
    assert response.status_code == 200
    data = response.json()
    assert data['queue_number'] == entry.queue_number
    assert 'ahead' in data and 'estimate' in data


def test_call_next_assigns_counter_and_notifies(staff_client, service, counter, student_user):
    entry = QueueEntry.objects.create(service=service, student=student_user, queue_number='FIN-A001', position=1)
    staff_client.post(reverse('call_next', args=[service.id]))
    entry.refresh_from_db()
    assert entry.status == 'CALLED'
    assert entry.counter == counter
    assert Notification.objects.filter(user=student_user).exists()


def test_mark_served_computes_waiting_time(staff_client, service, counter, student_user):
    now = timezone.now()
    entry = QueueEntry.objects.create(
        service=service,
        student=student_user,
        queue_number='FIN-A001',
        position=1,
        status='CALLED',
        join_time=now - timedelta(minutes=10),
        called_time=now - timedelta(minutes=3),
    )
    staff_client.post(reverse('mark_served', args=[entry.id]))
    entry.refresh_from_db()
    assert entry.status == 'COMPLETED'
    assert entry.waiting_time_minutes == 7


def test_mark_no_show(staff_client, service, counter, student_user):
    entry = QueueEntry.objects.create(service=service, student=student_user, queue_number='FIN-A001', position=1, status='CALLED')
    staff_client.post(reverse('mark_no_show', args=[entry.id]))
    entry.refresh_from_db()
    assert entry.status == 'NO_SHOW'