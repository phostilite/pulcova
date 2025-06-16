from django.contrib import admin

from .models import Service, ServiceInquiry

admin.site.register(Service)
admin.site.register(ServiceInquiry)