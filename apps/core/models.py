from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class SEOModel(models.Model):
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.TextField(max_length=160, blank=True)
    og_image = models.ImageField(upload_to='og_images/', blank=True, null=True)
    canonical_url = models.URLField(blank=True)
    
    class Meta:
        abstract = True


class PublishableModel(models.Model):
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True)
    
    class Meta:
        abstract = True
