from django.db import models
from django.urls import reverse
from apps.core.models import TimeStampedModel, SEOModel, PublishableModel
from apps.portfolio.models import Technology
from apps.blog.models import Tag


class Solution(TimeStampedModel, SEOModel, PublishableModel):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=200)
    problem_description = models.TextField()
    root_cause = models.TextField()
    solution_content = models.TextField()
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE, related_name='solutions')
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    helpful_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    related_solutions = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('solutions:solution_detail', kwargs={'slug': self.slug})
    
    class Meta:
        ordering = ['-helpful_count', '-created_at']


class CodeSnippet(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    code = models.TextField()
    language = models.CharField(max_length=50)
    tags = models.ManyToManyField(Tag, blank=True)
    
    def __str__(self):
        return self.title
