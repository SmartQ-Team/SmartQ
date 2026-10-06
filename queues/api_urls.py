from django.urls import path
from . import api_views as v
from accounts.api_views_registration import api_register

urlpatterns = [
    # auth
    path('csrf/', v.csrf_bootstrap, name='api_csrf'),
    path('register/', api_register, name='api_register'),
    path('login/', v.api_login, name='api_login'),
    path('logout/', v.api_logout, name='api_logout'),
    path('me/', v.api_me, name='api_me'),

    

    # student
    path('services/', v.api_services, name='api_services'),
    path('departments/', v.api_departments, name='api_departments'),
    path('services/<int:service_id>/join/', v.api_join_queue, name='api_join'),
    path('queue/my/', v.api_my_queue, name='api_my_queue'),
    path('queue/<int:entry_id>/cancel/', v.api_cancel_queue, name='api_cancel'),
    path('queue/<int:entry_id>/late/', v.api_mark_late, name='api_mark_late'),
    path('queue/status/<int:entry_id>/', v.api_queue_status, name='api_queue_status'),

    # notifications
    path('notifications/', v.api_notifications, name='api_notifications'),
    path('notifications/poll/', v.api_notifications_poll, name='api_notifications_poll'),
    path('notifications/read-all/', v.api_notifications_read_all, name='api_notifications_read_all'),

    # public board
    path('board/', v.api_board, name='api_board'),

    # staff
    path('staff/dashboard/', v.api_staff_dashboard, name='api_staff_dashboard'),
    path('staff/queue/<int:service_id>/', v.api_staff_queue, name='api_staff_queue'),
    path('staff/call-next/<int:service_id>/', v.api_call_next, name='api_call_next'),
    path('staff/entry/<int:entry_id>/arrived/', v.api_mark_arrived, name='api_mark_arrived'),
    path('staff/entry/<int:entry_id>/served/', v.api_mark_served, name='api_mark_served'),
    path('staff/entry/<int:entry_id>/no-show/', v.api_mark_no_show, name='api_mark_no_show'),
    path('staff/entry/<int:entry_id>/reschedule/', v.api_reschedule, name='api_reschedule'),
    path('staff/analytics/', v.api_analytics, name='api_analytics'),

    # report issue
    path('report/', v.api_report_issue, name='api_report_issue'),
]