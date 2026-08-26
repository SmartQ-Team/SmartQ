from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class QueueEntry(models.Model):
    STATUS_CHOICES = [
        ('WAITING', 'Waiting'),
        ('CALLED', 'Called'),
        ('ARRIVED', 'Arrived'),
        ('SERVING', 'Serving'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]

    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='queue_entries'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='queue_entries'
    )
    queue_number = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='WAITING'
    )
    position = models.PositiveIntegerField(default=0)
    join_time = models.DateTimeField(default=timezone.now)
    called_time = models.DateTimeField(null=True, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    service_start_time = models.DateTimeField(null=True, blank=True)
    completion_time = models.DateTimeField(null=True, blank=True)
    waiting_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    service_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    counter = models.ForeignKey(
        'services.Counter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='queue_entries'
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['join_time']

    def __str__(self):
        return f"{self.queue_number} - {self.student.username}"