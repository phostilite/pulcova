from django.contrib import admin

from .models import Technology, Project, GalleryImage

admin.site.register(Technology)
admin.site.register(Project)
admin.site.register(GalleryImage)