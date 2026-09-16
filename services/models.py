from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='services'
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    average_service_time_minutes = models.PositiveIntegerField(default=10)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.department.name} - {self.name}'


class Counter(models.Model):
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='counters'
    )
    name = models.CharField(max_length=60)
    staff_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='counters'
    )
    active = models.BooleanField(default=True)

    def clean(self):
        if self.staff_user_id:
            profile = getattr(self.staff_user, 'profile', None)
            if profile is not None and profile.department_id and profile.department_id != self.department_id:
                raise ValidationError(
                    {'staff_user': 'Staff member belongs to a different department than this counter.'}
                )

    def __str__(self):
        return f'{self.department.name} - {self.name}'