from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    student_number = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2',
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                role='STUDENT',
                student_number=self.cleaned_data['student_number'],
            )
        return user