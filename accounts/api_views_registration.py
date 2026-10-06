from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import login
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import StudentRegistrationForm
from .audit import log_action


def _me_payload(user):
    profile = getattr(user, 'profile', None)
    return {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'role': profile.role if profile else 'STUDENT',
        'department_id': profile.department_id if profile else None,
        'department_name': profile.department.name if profile and profile.department else None,
        'student_number': profile.student_number if profile else None,
        'is_staff_role': bool(profile and profile.role in ['STAFF', 'SUPERVISOR', 'ADMIN']),
        'unread_notifications': 0,
    }


@ensure_csrf_cookie
@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    form = StudentRegistrationForm(request.data)
    if not form.is_valid():
        return Response(form.errors, status=400)
    user = form.save()
    login(request, user)
    log_action(request, action='REGISTER', entity_type='User',
               entity_id=user.id, details=f'Student {user.username} registered.')
    return Response(_me_payload(user), status=201)