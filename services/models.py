from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='services'
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    average_service_time_minutes = models.PositiveIntegerField(default=10)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Counter(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='counters'
    )
    name = models.CharField(max_length=100)
    staff_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_counters'
    )
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name