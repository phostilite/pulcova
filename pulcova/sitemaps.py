from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.blog.models import Article
from apps.portfolio.models import Project


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'pages:home',
            'pages:about', 
            'pages:portfolio',
            'pages:services',
            'pages:solutions',
            'pages:blog',
            'pages:contact',
            'legal:privacy',
            'legal:terms',
            'legal:cookies',
            'legal:gdpr',
            'legal:refund',
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        # Higher priority for core pages
        high_priority_pages = ['pages:home', 'pages:about', 'pages:services']
        if item in high_priority_pages:
            return 1.0
        elif item.startswith('pages:'):
            return 0.8
        else:  # legal pages
            return 0.5

    def changefreq(self, item):
        if item == 'pages:home':
            return 'daily'
        elif item in ['pages:blog', 'pages:portfolio']:
            return 'weekly'  
        else:
            return 'monthly'


class ArticleSitemap(Sitemap):
    """Sitemap for blog articles"""
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def priority(self, obj):
        # Higher priority for featured articles
        return 0.9 if obj.is_featured else 0.7


class ProjectSitemap(Sitemap):
    """Sitemap for portfolio projects"""
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Project.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def priority(self, obj):
        # Higher priority for featured projects
        return 0.8 if obj.is_featured else 0.6
