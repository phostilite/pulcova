from django.db import models
from apps.core.models import TimeStampedModel, PublishableModel


class Service(TimeStampedModel, PublishableModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    detailed_content = models.TextField()
    icon = models.ImageField(upload_to='services/icons/', blank=True, null=True)
    price_range = models.CharField(max_length=100, blank=True)
    delivery_time = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    order_priority = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-order_priority', '-created_at']


class ServiceInquiry(TimeStampedModel):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('converted', 'Converted'),
        ('closed', 'Closed'),
    ]
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='inquiries')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    company = models.CharField(max_length=200, blank=True)
    budget_range = models.CharField(max_length=100, blank=True)
    project_description = models.TextField()
    timeline = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    def __str__(self):
        return f"{self.name} - {self.service.title}"
    
    class Meta:
        verbose_name_plural = "Service Inquiries"
        ordering = ['-created_at']
