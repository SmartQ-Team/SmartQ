from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import Profile
from services.models import Counter, Department, Service


class Command(BaseCommand):
    help = 'Seed SmartQ with demo departments, services, counters and users (idempotent).'

    def handle(self, *args, **options):
        password = 'Capstone2026!'

        dept_specs = {
            'Finance Office': {
                'location': 'Admin Building',
                'services': ['Fee Enquiry', 'NSFAS Enquiry'],
                'staff': 'staff_finance',
            },
            'Health Clinic': {
                'location': 'Campus Clinic',
                'services': ['Clinic Consultation'],
                'staff': 'staff_clinic',
            },
            'ICT Support': {
                'location': 'Chemistry Building',
                'services': ['PC Troubleshooting', 'Technical Services'],
                'staff': 'staff_ict',
            },
        }

        for dept_name, spec in dept_specs.items():
            dept, _ = Department.objects.get_or_create(
                name=dept_name, defaults={'location': spec['location']}
            )
            for svc in spec['services']:
                Service.objects.get_or_create(department=dept, name=svc)
            for i in range(1, 3):
                Counter.objects.get_or_create(department=dept, name=f'Counter {i}')

            staff_user, created = User.objects.get_or_create(
                username=spec['staff'], defaults={'email': f"{spec['staff']}@ufh.ac.za"}
            )
            if created:
                staff_user.set_password(password)
                staff_user.save()
            Profile.objects.get_or_create(
                user=staff_user, defaults={'role': 'STAFF', 'department': dept}
            )

        for i in range(1, 4):
            username = f'student{i}'
            u, created = User.objects.get_or_create(
                username=username, defaults={'email': f'{username}@ufh.ac.za'}
            )
            if created:
                u.set_password(password)
                u.save()
            Profile.objects.get_or_create(user=u, defaults={'role': 'STUDENT'})

        self.stdout.write(self.style.SUCCESS('Demo data ready.'))
        self.stdout.write(f'Staff:   staff_finance / staff_clinic / staff_ict  (pw: {password})')
        self.stdout.write(f'Students: student1 .. student3                   (pw: {password})')