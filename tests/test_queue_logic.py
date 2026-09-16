from datetime import timedelta

import pytest
from django.utils import timezone

from queues import queue_logic
from queues.models import QueueEntry
from services.models import Service

pytestmark = pytest.mark.django_db


def test_generate_queue_number_format(service, student_user):
    number = queue_logic.generate_queue_number(service)
    assert number.startswith('FIN-A')
    assert number.endswith('001')


def test_waiting_list_is_fifo(service, student_user):
    e1 = QueueEntry.objects.create(service=service, student=student_user, queue_number='A1', position=1)
    e2 = QueueEntry.objects.create(service=service, student=student_user, queue_number='A2', position=2)
    QueueEntry.objects.filter(id=e1.id).update(join_time=timezone.now() - timedelta(minutes=5))
    assert list(queue_logic.waiting_list(service)) == [e1, e2]


def test_students_ahead(service, student_user):
    e1 = QueueEntry.objects.create(service=service, student=student_user, queue_number='A1', position=1)
    e2 = QueueEntry.objects.create(service=service, student=student_user, queue_number='A2', position=2)
    QueueEntry.objects.filter(id=e2.id).update(join_time=timezone.now() + timedelta(seconds=1))
    assert queue_logic.students_ahead(e2) == 1


def test_rule_based_estimate(service, counter):
    # 6 ahead x 10 min / 1 counter = 60
    assert queue_logic.estimate_waiting_time(service, 6) == 60


def test_congestion_moderate_at_10_waiting(department, student_user):
    fast_service = Service.objects.create(
        department=department, name='Quick Query', average_service_time_minutes=4,
    )
    for i in range(10):
        QueueEntry.objects.create(service=fast_service, student=student_user, queue_number=f'A{i}', position=i + 1)
    assert queue_logic.congestion_status(fast_service)['label'] == 'Moderate'


def test_congestion_congested_when_estimate_exceeds_45(service, student_user):
    for i in range(10):
        QueueEntry.objects.create(service=service, student=student_user, queue_number=f'A{i}', position=i + 1)
    assert queue_logic.congestion_status(service)['label'] == 'Congested'

def test_congestion_normal_when_empty(service):
    assert queue_logic.congestion_status(service)['label'] == 'Normal'