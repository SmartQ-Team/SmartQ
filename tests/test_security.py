import pytest
from django.urls import reverse

from accounts.models import AuditLog
from queues.models import QueueEntry

pytestmark = pytest.mark.django_db


def test_student_cannot_open_staff_dashboard(student_client):
    response = student_client.get(reverse('staff_dashboard'))
    assert response.status_code in (302, 403)


def test_student_cannot_call_next(student_client, service):
    response = student_client.post(reverse('call_next', args=[service.id]))
    assert response.status_code in (302, 403)


def test_anonymous_cannot_join_queue(client, service):
    response = client.post(reverse('join_queue', args=[service.id]))
    assert response.status_code == 302
    assert QueueEntry.objects.count() == 0


def test_audit_log_written_on_join(student_client, service):
    student_client.post(reverse('join_queue', args=[service.id]))
    assert AuditLog.objects.filter(action='QUEUE_JOIN').exists()


def test_audit_log_on_call_next(staff_client, service, counter, student_user):
    QueueEntry.objects.create(service=service, student=student_user, queue_number='FIN-A001', position=1)
    staff_client.post(reverse('call_next', args=[service.id]))
    assert AuditLog.objects.filter(action='CALL_NEXT').exists()