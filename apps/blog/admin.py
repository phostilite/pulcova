from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Category, Tag, Article, Newsletter


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'article_count', 'created_at']
    list_filter = ['created_at', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'article_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def article_count(self, obj):
        return obj.article_set.count()
    article_count.short_description = 'Articles'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_published', 'is_featured', 'view_count', 'published_at']
    list_filter = ['is_published', 'is_featured', 'category', 'created_at', 'published_at']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    date_hierarchy = 'published_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category', 'tags')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('Publishing', {
            'fields': ('is_published', 'published_at', 'is_featured')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('reading_time', 'view_count'),
            'classes': ('collapse',)
        })
    )


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'source', 'subscription_date', 'unsubscribe_link']
    list_filter = ['is_active', 'source', 'subscription_date']
    search_fields = ['email']
    readonly_fields = ['subscription_date', 'unsubscribe_token', 'unsubscribe_link']
    date_hierarchy = 'subscription_date'
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions', 'export_emails']
    
    def unsubscribe_link(self, obj):
        if obj.unsubscribe_token:
            url = reverse('blog:newsletter_unsubscribe_token', args=[obj.unsubscribe_token])
            return format_html(
                '<a href="{}" target="_blank" class="button">Unsubscribe Link</a>',
                url
            )
        return '-'
    unsubscribe_link.short_description = 'Unsubscribe'
    
    def activate_subscriptions(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} subscriptions were activated.')
    activate_subscriptions.short_description = 'Activate selected subscriptions'
    
    def deactivate_subscriptions(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} subscriptions were deactivated.')
    deactivate_subscriptions.short_description = 'Deactivate selected subscriptions'
    
    def export_emails(self, request, queryset):
        emails = list(queryset.filter(is_active=True).values_list('email', flat=True))
        email_list = ', '.join(emails)
        self.message_user(request, f'Active emails ({len(emails)}): {email_list}')
    export_emails.short_description = 'Export active email addresses'