import pytest

from queues.models import QueueEntry

pytestmark = pytest.mark.django_db


def test_queue_entry_str(old_entry):
    assert str(old_entry) == 'FIN-A001 - student1'


def test_default_status_is_waiting(old_entry):
    assert old_entry.status == 'WAITING'


def test_profile_role_created(student_user):
    assert student_user.profile.role == 'STUDENT'


def test_counters_at_join_recorded(student_client, service, student_user):
    from django.urls import reverse
    student_client.post(reverse('join_queue', args=[service.id]))
    entry = QueueEntry.objects.get(student=student_user)
    assert entry.counters_at_join >= 1