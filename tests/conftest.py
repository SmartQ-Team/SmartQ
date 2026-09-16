from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from accounts.models import Profile
from queues import ml_model
from services.models import Counter, Department, Service


@pytest.fixture(autouse=True)
def disable_ml(monkeypatch):
    """Force rule-based estimates so tests are deterministic."""
    monkeypatch.setattr(ml_model, 'load_model', lambda: None)


@pytest.fixture
def department(db):
    return Department.objects.create(name='Finance Office', location='Admin Block')


@pytest.fixture
def student_user(db):
    user = User.objects.create_user('student1', password='pass12345')
    Profile.objects.create(user=user, role='STUDENT', student_number='20201234')
    return user


@pytest.fixture
def staff_user(db, department):
    user = User.objects.create_user('staff1', password='pass12345')
    Profile.objects.create(user=user, role='STAFF', department=department)
    return user


@pytest.fixture
def service(department):
    return Service.objects.create(
        department=department,
        name='Fee Enquiry',
        average_service_time_minutes=10,
    )


@pytest.fixture
def counter(department, staff_user):
    return Counter.objects.create(
        department=department,
        name='Counter 1',
        staff_user=staff_user,
        active=True,
    )


@pytest.fixture
def student_client(client, student_user):
    client.login(username='student1', password='pass12345')
    return client


@pytest.fixture
def staff_client(client, staff_user):
    client.login(username='staff1', password='pass12345')
    return client


@pytest.fixture
def old_entry(service, student_user):
    from queues.models import QueueEntry
    return QueueEntry.objects.create(
        service=service,
        student=student_user,
        queue_number='FIN-A001',
        position=1,
    )