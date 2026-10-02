from rest_framework import serializers
from .models import QueueEntry


class QueueEntrySerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_id = serializers.IntegerField(source='service.id', read_only=True)
    department_name = serializers.CharField(source='service.department.name', read_only=True)
    department_location = serializers.CharField(source='service.department.location', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)
    counter_name = serializers.CharField(source='counter.name', read_only=True, default=None)

    class Meta:
        model = QueueEntry
        fields = [
            'id', 'queue_number', 'status', 'status_display',
            'position', 'running_late',
            'join_time', 'called_time', 'arrival_time',
            'completion_time', 'waiting_time_minutes',
            'service_id', 'service_name',
            'department_name', 'department_location',
            'student_username', 'counter_name',
        ]