from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import EmailValidator
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


class Newsletter(TimeStampedModel):
    """
    Model to store newsletter subscriptions
    """
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Email address for newsletter subscription"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the subscription is active"
    )
    subscription_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date when the subscription was created"
    )
    unsubscribe_token = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        help_text="Token for unsubscribing"
    )
    source = models.CharField(
        max_length=50,
        default='blog',
        help_text="Source of subscription (e.g., blog, footer, popup)"
    )
    
    def __str__(self):
        return f"{self.email} - {'Active' if self.is_active else 'Inactive'}"
    
    def save(self, *args, **kwargs):
        # Generate unsubscribe token if not provided
        if not self.unsubscribe_token:
            import secrets
            self.unsubscribe_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-subscription_date']
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"


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
    
    def get_absolute_url(self):
        return reverse('blog:article_detail', kwargs={'slug': self.slug})
    
    class Meta:
        ordering = ['-published_at', '-created_at']