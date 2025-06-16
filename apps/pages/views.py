from django.views.generic import TemplateView
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from apps.blog.models import Article, Category, Tag
from apps.portfolio.models import Project, Technology
import logging

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    """
    Class-based view for the home page.
    """
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        """
        Add recent blog posts and featured projects to the context with proper error handling.
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
        
        try:
            # Get featured projects
            featured_projects = Project.objects.select_related().prefetch_related(
                'tech_stack'
            ).filter(
                is_featured=True,
                is_published=True,
                published_at__lte=timezone.now()
            ).order_by('-order_priority', '-created_at')[:5]  # Get top 5 featured projects
            
            context['featured_projects'] = featured_projects
            
        except Exception as e:
            logger.error(f"Error fetching featured projects for home page: {e}")
            # Set empty queryset as fallback
            context['featured_projects'] = Project.objects.none()
        
        return context
    
    
class AboutView(TemplateView):
    """
    Class-based view for the about page.
    """
    template_name = 'pages/about.html'
    
    
class PortfolioView(TemplateView):
    """
    Class-based view for the portfolio page with real portfolio data.
    """
    template_name = 'pages/portfolio.html'
    
    def get_context_data(self, **kwargs):
        """
        Add portfolio data to the context with proper error handling.
        """
        context = super().get_context_data(**kwargs)
        
        try:
            # Get all published projects with optimized queries
            all_projects = Project.objects.select_related().prefetch_related(
                'tech_stack', 'gallery_images'
            ).filter(
                is_published=True,
                published_at__lte=timezone.now()
            ).order_by('-order_priority', '-is_featured', '-created_at')
            
            # Handle project type filter
            project_type = self.request.GET.get('type', '').strip()
            if project_type and project_type != 'all':
                all_projects = all_projects.filter(project_type=project_type)
                context['current_type'] = project_type
            
            # Handle technology filter
            tech_filter = self.request.GET.get('tech', '').strip()
            if tech_filter:
                try:
                    technology = Technology.objects.get(slug=tech_filter)
                    all_projects = all_projects.filter(tech_stack=technology)
                    context['current_tech'] = tech_filter
                except Technology.DoesNotExist:
                    logger.warning(f"Technology with slug '{tech_filter}' not found")
            
            # Handle year filter
            year_filter = self.request.GET.get('year', '').strip()
            if year_filter:
                if year_filter == 'older':
                    all_projects = all_projects.filter(start_date__year__lt=2022)
                else:
                    try:
                        year = int(year_filter)
                        all_projects = all_projects.filter(start_date__year=year)
                        context['current_year'] = year_filter
                    except ValueError:
                        logger.warning(f"Invalid year filter: {year_filter}")
            
            # Handle search query
            search_query = self.request.GET.get('search', '').strip()
            if search_query:
                all_projects = all_projects.filter(
                    Q(title__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(detailed_content__icontains=search_query)
                )
                context['current_search'] = search_query
            
            # Pagination
            paginate_by = 12
            page = self.request.GET.get('page', 1)
            
            try:
                paginator = Paginator(all_projects, paginate_by)
                projects = paginator.page(page)
            except PageNotAnInteger:
                projects = paginator.page(1)
            except EmptyPage:
                projects = paginator.page(paginator.num_pages)
            
            context['projects'] = projects
            context['total_projects'] = all_projects.count()
            
            # Get featured projects for hero section
            try:
                featured_projects = Project.objects.select_related().prefetch_related(
                    'tech_stack'
                ).filter(
                    is_featured=True,
                    is_published=True,
                    published_at__lte=timezone.now()
                ).order_by('-order_priority', '-created_at')[:3]
                
                context['featured_projects'] = featured_projects
                context['has_featured'] = featured_projects.exists()
                
            except Exception as e:
                logger.error(f"Error fetching featured projects: {e}")
                context['featured_projects'] = Project.objects.none()
                context['has_featured'] = False
            
            # Get project types with counts
            try:
                project_types = Project.objects.filter(
                    is_published=True,
                    published_at__lte=timezone.now()
                ).values('project_type').annotate(
                    count=Count('id')
                ).order_by('project_type')
                
                # Convert to dict for easier template usage
                project_type_counts = {item['project_type']: item['count'] for item in project_types}
                context['project_type_counts'] = project_type_counts
                
                # Get available project types
                available_types = list(project_type_counts.keys())
                context['available_types'] = available_types
                
            except Exception as e:
                logger.error(f"Error fetching project types: {e}")
                context['project_type_counts'] = {}
                context['available_types'] = []
            
            # Get technologies with project counts
            try:
                technologies = Technology.objects.filter(
                    project__is_published=True,
                    project__published_at__lte=timezone.now()
                ).annotate(
                    project_count=Count('project', distinct=True)
                ).filter(
                    project_count__gt=0
                ).order_by('-project_count', 'name')[:20]  # Top 20 most used technologies
                
                context['technologies'] = technologies
                context['has_technologies'] = technologies.exists()
                
            except Exception as e:
                logger.error(f"Error fetching technologies: {e}")
                context['technologies'] = Technology.objects.none()
                context['has_technologies'] = False
            
            # Get available years from project start dates
            try:
                years = Project.objects.filter(
                    is_published=True,
                    published_at__lte=timezone.now(),
                    start_date__isnull=False
                ).dates('start_date', 'year', order='DESC')
                
                available_years = [date.year for date in years]
                context['available_years'] = available_years
                
            except Exception as e:
                logger.error(f"Error fetching available years: {e}")
                context['available_years'] = []
            
            # Add statistics for display
            try:
                stats = {
                    'total_projects': Project.objects.filter(is_published=True).count(),
                    'total_technologies': Technology.objects.filter(
                        project__is_published=True
                    ).distinct().count(),
                    'featured_projects': Project.objects.filter(
                        is_published=True, is_featured=True
                    ).count(),
                }
                context['stats'] = stats
                
            except Exception as e:
                logger.error(f"Error calculating portfolio statistics: {e}")
                context['stats'] = {
                    'total_projects': 0,
                    'total_technologies': 0,
                    'featured_projects': 0,
                }
            
            # Add current filters for template
            context['current_filters'] = {
                'type': project_type if project_type else 'all',
                'tech': tech_filter,
                'year': year_filter,
                'search': search_query,
            }
            
            # Add filter status
            has_active_filters = any([
                project_type and project_type != 'all',
                tech_filter,
                year_filter,
                search_query
            ])
            context['has_active_filters'] = has_active_filters
            
        except Exception as e:
            logger.error(f"Error building context for portfolio page: {e}")
            # Provide safe defaults in case of major errors
            context.update({
                'projects': Project.objects.none(),
                'total_projects': 0,
                'featured_projects': Project.objects.none(),
                'has_featured': False,
                'project_type_counts': {},
                'available_types': [],
                'technologies': Technology.objects.none(),
                'has_technologies': False,
                'available_years': [],
                'stats': {
                    'total_projects': 0,
                    'total_technologies': 0,
                    'featured_projects': 0,
                },
                'current_filters': {
                    'type': 'all',
                    'tech': '',
                    'year': '',
                    'search': '',
                },
                'has_active_filters': False,
            })
        
        return context


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