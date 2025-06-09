from django.db import models
from apps.core.models import TimeStampedModel, SEOModel, PublishableModel


class Technology(TimeStampedModel):
    CATEGORY_CHOICES = [
        ('frontend', 'Frontend'),
        ('backend', 'Backend'),
        ('devops', 'DevOps'),
        ('database', 'Database'),
        ('mobile', 'Mobile'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='tech_icons/', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Technologies"


class Project(TimeStampedModel, SEOModel, PublishableModel):
    PROJECT_TYPE_CHOICES = [
        ('web', 'Web Application'),
        ('mobile', 'Mobile Application'),
        ('api', 'API/Backend'),
        ('desktop', 'Desktop Application'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    detailed_content = models.TextField()
    featured_image = models.ImageField(upload_to='projects/featured/', blank=True, null=True)
    gallery_images = models.ManyToManyField('GalleryImage', blank=True)
    tech_stack = models.ManyToManyField(Technology, blank=True)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default='web')
    live_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    order_priority = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-order_priority', '-created_at']


class GalleryImage(TimeStampedModel):
    image = models.ImageField(upload_to='projects/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"Gallery Image {self.id}"
