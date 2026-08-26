from django.contrib import admin
from .models import Department, Service, Counter

admin.site.register(Department)
admin.site.register(Service)
admin.site.register(Counter)