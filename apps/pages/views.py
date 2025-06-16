from django.views.generic import TemplateView
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from apps.blog.models import Article, Category, Tag
import logging

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    """
    Class-based view for the home page.
    """
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        """
        Add recent blog posts to the context with proper error handling.
        """
        context = super().get_context_data(**kwargs)
        
        try:
            # Get the latest published blog posts
            recent_blogs = Article.objects.select_related(
                'author', 
                'category'
            ).prefetch_related(
                'tags'
            ).filter(
                is_published=True,
                published_at__lte=timezone.now()
            ).order_by('-published_at')[:3]  # Get latest 3 posts
            
            context['recent_blogs'] = recent_blogs
            
        except Exception as e:
            logger.error(f"Error fetching recent blog posts for home page: {e}")
            # Set empty queryset as fallback
            context['recent_blogs'] = Article.objects.none()
        
        return context
    
    
class AboutView(TemplateView):
    """
    Class-based view for the about page.
    """
    template_name = 'pages/about.html'
    
    
class PortfolioView(TemplateView):
    """
    Class-based view for the portfolio page.
    """
    template_name = 'pages/portfolio.html'


class BlogView(TemplateView):
    """
    Class-based view for the blog page with real blog data.
    """
    template_name = 'pages/blog.html'
    
    def get_context_data(self, **kwargs):
        """
        Add real blog data to the context with proper error handling.
        """
        context = super().get_context_data(**kwargs)
        
        try:
            # Get all published blog posts
            all_blogs = Article.objects.select_related(
                'author', 
                'category'
            ).prefetch_related(
                'tags'
            ).filter(
                is_published=True,
                published_at__lte=timezone.now()
            ).order_by('-published_at')
            
            # Handle search query
            search_query = self.request.GET.get('search', '').strip()
            if search_query:
                all_blogs = all_blogs.filter(
                    Q(title__icontains=search_query) |
                    Q(excerpt__icontains=search_query) |
                    Q(content__icontains=search_query)
                )
                context['current_search'] = search_query
            
            # Handle category filter
            category_slug = self.request.GET.get('category', '').strip()
            if category_slug:
                try:
                    category = Category.objects.get(slug=category_slug)
                    all_blogs = all_blogs.filter(category=category)
                    context['current_category'] = category_slug
                except Category.DoesNotExist:
                    logger.warning(f"Category with slug '{category_slug}' not found")
            
            # Handle tag filter
            tag_slug = self.request.GET.get('tag', '').strip()
            if tag_slug:
                try:
                    tag = Tag.objects.get(slug=tag_slug)
                    all_blogs = all_blogs.filter(tags=tag)
                    context['current_tag'] = tag_slug
                except Tag.DoesNotExist:
                    logger.warning(f"Tag with slug '{tag_slug}' not found")
            
            # Get featured articles (first 2 featured or latest 2 if no featured)
            try:
                featured_blogs = all_blogs.filter(is_featured=True)[:2]
                if not featured_blogs.exists():
                    featured_blogs = all_blogs[:2]
                context['featured_blogs'] = featured_blogs
            except Exception as e:
                logger.error(f"Error fetching featured blogs: {e}")
                context['featured_blogs'] = Article.objects.none()
            
            # Get recent blogs (excluding featured ones)
            try:
                featured_ids = list(featured_blogs.values_list('id', flat=True)) if 'featured_blogs' in context else []
                recent_blogs = all_blogs.exclude(id__in=featured_ids)
                context['recent_blogs'] = recent_blogs
            except Exception as e:
                logger.error(f"Error fetching recent blogs: {e}")
                context['recent_blogs'] = Article.objects.none()
            
            # Get categories with article counts
            try:
                categories = Category.objects.filter(
                    articles__is_published=True,
                    articles__published_at__lte=timezone.now()
                ).distinct().order_by('name')
                context['categories'] = categories
            except Exception as e:
                logger.error(f"Error fetching categories: {e}")
                context['categories'] = Category.objects.none()
            
            # Get popular tags
            try:
                popular_tags = Tag.objects.filter(
                    article__is_published=True,
                    article__published_at__lte=timezone.now()
                ).distinct().order_by('name')[:20]
                context['popular_tags'] = popular_tags
            except Exception as e:
                logger.error(f"Error fetching popular tags: {e}")
                context['popular_tags'] = Tag.objects.none()
            
            # Add total count for reference
            context['total_blogs'] = all_blogs.count() if all_blogs else 0
            
        except Exception as e:
            logger.error(f"Error building context for blog page: {e}")
            # Provide empty defaults in case of major errors
            context.update({
                'featured_blogs': Article.objects.none(),
                'recent_blogs': Article.objects.none(),
                'categories': Category.objects.none(),
                'popular_tags': Tag.objects.none(),
                'total_blogs': 0,
            })
        
        return context


class SolutionsView(TemplateView):
    """
    Class-based view for the solutions page.
    """
    template_name = 'pages/solutions.html'


class ServicesView(TemplateView):
    """
    Class-based view for the services page.
    """
    template_name = 'pages/services.html'
    
    
class ContactView(TemplateView):
    """
    Class-based view for the contact page.
    """
    template_name = 'pages/contact.html'