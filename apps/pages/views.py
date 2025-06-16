from django.views.generic import TemplateView
from django.utils import timezone
from apps.blog.models import Article
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
    Class-based view for the blog page.
    """
    template_name = 'pages/blog.html'


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