# accounts/api_views_registration.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import login
from .forms import StudentRegistrationForm
from .audit import log_action

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    form = StudentRegistrationForm(request.data)
    if not form.is_valid():
        return Response(form.errors, status=400)
    user = form.save()
    login(request, user)
    log_action(request, action='REGISTER', entity_type='User', entity_id=user.id,
               details=f'Student {user.username} registered.')
    return Response({'ok': True}, status=201)