from django.contrib import admin

from .models import AuditLog, Notification, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'student_number', 'department')
    list_filter = ('role',)
    search_fields = ('user__username', 'student_number')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'read')
    list_filter = ('read',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'entity_type', 'entity_id', 'ip_address')
    list_filter = ('action',)
    search_fields = ('user__username', 'details')
    readonly_fields = ('user', 'action', 'entity_type', 'entity_id', 'details', 'ip_address', 'timestamp')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False