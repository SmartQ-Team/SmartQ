from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # --- ADD THESE TWO LINES FOR LOGIN/LOGOUT ---
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # --------------------------------------------

    path('register/', views.register, name='register'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read-all/', views.notifications_read_all, name='notifications_read_all'),
    path('notifications/api/', views.notifications_api, name='notifications_api'),
    path('report/', views.report_issue, name='report_issue'),
]