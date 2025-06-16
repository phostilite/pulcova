from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from apps.core.models import TimeStampedModel, SEOModel, PublishableModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"


class Tag(TimeStampedModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name


class Article(TimeStampedModel, SEOModel, PublishableModel):
    title = models.CharField(max_length=200)
    excerpt = models.TextField(max_length=300)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='articles/featured/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')
    tags = models.ManyToManyField(Tag, blank=True)
    reading_time = models.PositiveIntegerField(default=5)  # in minutes
    is_featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-published_at', '-created_at']