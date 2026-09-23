from django.urls import path

from . import views

urlpatterns = [
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('queue/join/<int:service_id>/', views.join_queue, name='join_queue'),
    path('queue/my/', views.my_queue, name='my_queue'),
    path('queue/cancel/<int:entry_id>/', views.cancel_queue, name='cancel_queue'),
    path('queue/late/<int:entry_id>/', views.mark_late, name='mark_late'),
    path('queue/api/status/<int:entry_id>/', views.queue_status_api, name='queue_status_api'),
    path('board/', views.board, name='board'),
    path('board/api/', views.board_api, name='board_api'),
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/api/dashboard/', views.staff_dashboard_api, name='staff_dashboard_api'),
    path('staff/api/queue/<int:service_id>/', views.staff_queue_api, name='staff_queue_api'),
    path('staff/queue/<int:service_id>/', views.staff_queue, name='staff_queue'),
    path('staff/call-next/<int:service_id>/', views.call_next, name='call_next'),
    path('staff/entry/<int:entry_id>/arrived/', views.mark_arrived, name='mark_arrived'),
    path('staff/entry/<int:entry_id>/served/', views.mark_served, name='mark_served'),
    path('staff/entry/<int:entry_id>/no-show/', views.mark_no_show, name='mark_no_show'),
    path('staff/entry/<int:entry_id>/reschedule/', views.reschedule_entry, name='reschedule_entry'),
    path('staff/analytics/', views.analytics, name='analytics'),
]