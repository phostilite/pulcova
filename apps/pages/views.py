from django.views.generic import TemplateView, FormView
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Sum
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from apps.blog.models import Article, Category, Tag
from apps.portfolio.models import Project, Technology
from .forms import ContactForm
import logging
import traceback

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
    Class-based view for the solutions page with real solutions data.
    """
    template_name = 'pages/solutions.html'
    
    def get_context_data(self, **kwargs):
        """
        Add solutions data to the context with proper error handling.
        """
        context = super().get_context_data(**kwargs)
        
        try:
            # Import here to avoid circular imports
            from apps.solutions.models import Solution, CodeSnippet
            
            # Get all published solutions
            all_solutions = Solution.objects.select_related(
                'technology'
            ).prefetch_related(
                'related_solutions__technology'
            ).filter(
                is_published=True,
                published_at__lte=timezone.now()
            ).order_by('-helpful_count', '-created_at')
            
            # Handle search query
            search_query = self.request.GET.get('search', '').strip()
            if search_query:
                all_solutions = all_solutions.filter(
                    Q(title__icontains=search_query) |
                    Q(problem_description__icontains=search_query) |
                    Q(solution_content__icontains=search_query) |
                    Q(technology__name__icontains=search_query)
                )
            
            # Handle technology filter
            tech_filter = self.request.GET.get('tech', '').strip()
            if tech_filter:
                try:
                    all_solutions = all_solutions.filter(technology__slug=tech_filter)
                except Exception as e:
                    logger.error(f"Error filtering by technology: {e}")
            
            # Handle difficulty filter
            difficulty_filter = self.request.GET.get('difficulty', '').strip()
            if difficulty_filter and difficulty_filter != 'all':
                try:
                    all_solutions = all_solutions.filter(difficulty_level=difficulty_filter)
                except Exception as e:
                    logger.error(f"Error filtering by difficulty: {e}")
            
            # Handle sorting
            sort_by = self.request.GET.get('sort', 'helpful').strip()
            if sort_by == 'newest':
                all_solutions = all_solutions.order_by('-created_at')
            elif sort_by == 'views':
                all_solutions = all_solutions.order_by('-view_count', '-created_at')
            elif sort_by == 'title':
                all_solutions = all_solutions.order_by('title')
            else:  # default to helpful
                all_solutions = all_solutions.order_by('-helpful_count', '-created_at')
            
            # Pagination
            paginate_by = 12
            page = self.request.GET.get('page', 1)
            
            try:
                paginator = Paginator(all_solutions, paginate_by)
                solutions = paginator.page(page)
            except PageNotAnInteger:
                solutions = paginator.page(1)
            except EmptyPage:
                solutions = paginator.page(paginator.num_pages)
            
            context['solutions'] = solutions
            context['total_solutions'] = all_solutions.count()
            
            # Get featured solutions for hero section
            try:
                featured_solutions = Solution.objects.select_related(
                    'technology'
                ).filter(
                    is_published=True,
                    published_at__lte=timezone.now(),
                    helpful_count__gte=5  # Consider solutions with 5+ helpful votes as featured
                ).order_by('-helpful_count', '-view_count')[:6]
                
                context['featured_solutions'] = featured_solutions
                context['has_featured'] = featured_solutions.exists()
                
            except Exception as e:
                logger.error(f"Error fetching featured solutions: {e}")
                context['featured_solutions'] = Solution.objects.none()
                context['has_featured'] = False
            
            # Get technologies with solution counts
            try:
                from apps.portfolio.models import Technology
                technologies = Technology.objects.annotate(
                    solution_count=Count('solutions', filter=Q(
                        solutions__is_published=True,
                        solutions__published_at__lte=timezone.now()
                    ))
                ).filter(
                    solution_count__gt=0
                ).order_by('-solution_count', 'name')
                
                context['technologies'] = technologies
                context['has_technologies'] = technologies.exists()
                
            except Exception as e:
                logger.error(f"Error fetching technologies: {e}")
                context['technologies'] = []
                context['has_technologies'] = False
            
            # Get difficulty level counts
            try:
                difficulty_counts = {}
                for choice_value, choice_label in Solution.DIFFICULTY_CHOICES:
                    count = all_solutions.filter(difficulty_level=choice_value).count()
                    if count > 0:
                        difficulty_counts[choice_value] = {
                            'label': choice_label,
                            'count': count
                        }
                
                context['difficulty_counts'] = difficulty_counts
                
            except Exception as e:
                logger.error(f"Error calculating difficulty counts: {e}")
                context['difficulty_counts'] = {}
            
            # Get recent code snippets
            try:
                code_snippets = CodeSnippet.objects.prefetch_related(
                    'tags'
                ).order_by('-created_at')[:6]
                
                context['code_snippets'] = code_snippets
                context['has_code_snippets'] = code_snippets.exists()
                
            except Exception as e:
                logger.error(f"Error fetching code snippets: {e}")
                context['code_snippets'] = CodeSnippet.objects.none()
                context['has_code_snippets'] = False
            
            # Add statistics for display
            try:
                total_solutions_count = Solution.objects.filter(
                    is_published=True,
                    published_at__lte=timezone.now()
                ).count()
                
                total_technologies_count = Technology.objects.filter(
                    solutions__is_published=True,
                    solutions__published_at__lte=timezone.now()
                ).distinct().count()
                
                total_votes = Solution.objects.filter(
                    is_published=True,
                    published_at__lte=timezone.now()
                ).aggregate(
                    total_helpful=Sum('helpful_count')
                )['total_helpful'] or 0
                
                total_views = Solution.objects.filter(
                    is_published=True,
                    published_at__lte=timezone.now()
                ).aggregate(
                    total_views=Sum('view_count')
                )['total_views'] or 0
                
                context['stats'] = {
                    'total_solutions': total_solutions_count,
                    'total_technologies': total_technologies_count,
                    'total_votes': total_votes,
                    'total_views': total_views,
                }
                
            except Exception as e:
                logger.error(f"Error calculating statistics: {e}")
                context['stats'] = {
                    'total_solutions': 0,
                    'total_technologies': 0,
                    'total_votes': 0,
                    'total_views': 0,
                }
            
            # Add current filters for template
            context['current_filters'] = {
                'search': search_query,
                'tech': tech_filter,
                'difficulty': difficulty_filter if difficulty_filter else 'all',
                'sort': sort_by,
            }
            
            # Add filter status
            has_active_filters = any([
                search_query,
                tech_filter,
                difficulty_filter and difficulty_filter != 'all',
            ])
            context['has_active_filters'] = has_active_filters
            
        except Exception as e:
            logger.error(f"Error building context for solutions page: {e}")
            # Provide safe defaults in case of major errors
            context.update({
                'solutions': [],
                'total_solutions': 0,
                'featured_solutions': [],
                'has_featured': False,
                'technologies': [],
                'has_technologies': False,
                'difficulty_counts': {},
                'code_snippets': [],
                'has_code_snippets': False,
                'stats': {
                    'total_solutions': 0,
                    'total_technologies': 0,
                    'total_votes': 0,
                    'total_views': 0,
                },
                'current_filters': {
                    'search': '',
                    'tech': '',
                    'difficulty': 'all',
                    'sort': 'helpful',
                },
                'has_active_filters': False,
            })
        
        return context


class ServicesView(TemplateView):
    """
    Class-based view for the services page with real services data and form handling.
    """
    template_name = 'pages/services.html'
    
    def post(self, request, *args, **kwargs):
        """
        Handle service inquiry form submission.
        """
        try:
            # Import here to avoid circular imports
            from apps.services.models import Service, ServiceInquiry
            
            # Extract form data
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            service_id = request.POST.get('service', '').strip()
            company = request.POST.get('company', '').strip()
            budget_range = request.POST.get('budget_range', '').strip()
            timeline = request.POST.get('timeline', '').strip()
            project_description = request.POST.get('project_description', '').strip()
            
            # Basic validation
            if not all([name, email, project_description]):
                messages.error(request, 'Please fill in all required fields (Name, Email, and Project Description).')
                return self.get(request, *args, **kwargs)
            
            if not service_id or service_id == 'other':
                # Handle "other" service type
                try:
                    # Create a generic service entry or handle differently
                    service = None
                except Exception:
                    service = None
            else:
                try:
                    service = Service.objects.get(id=service_id, is_active=True, is_published=True)
                except Service.DoesNotExist:
                    messages.error(request, 'Invalid service selected. Please choose a valid service.')
                    return self.get(request, *args, **kwargs)
                except ValueError:
                    # Handle invalid service_id format
                    messages.error(request, 'Invalid service selected. Please choose a valid service.')
                    return self.get(request, *args, **kwargs)
            
            # Create service inquiry
            if service:
                inquiry = ServiceInquiry.objects.create(
                    service=service,
                    name=name,
                    email=email,
                    company=company,
                    budget_range=budget_range,
                    project_description=project_description,
                    timeline=timeline,
                    status='new'
                )
                
                messages.success(request, 
                    f'Thank you {name}! Your inquiry for "{service.title}" has been submitted successfully. '
                    'I will review your requirements and get back to you within 24 hours.')
            else:
                # Handle "other" service inquiries - you might want to create a generic service
                # or handle this differently based on your requirements
                messages.success(request, 
                    f'Thank you {name}! Your custom service inquiry has been submitted successfully. '
                    'I will review your requirements and get back to you within 24 hours.')
            
            # Log the successful inquiry
            logger.info(f"New service inquiry submitted by {email} for service: {service.title if service else 'Custom'}")
            
            # Redirect to prevent form resubmission
            return HttpResponseRedirect(reverse('pages:services') + '#contact')
            
        except Exception as e:
            logger.error(f"Error processing service inquiry: {e}", exc_info=True)
            messages.error(request, 'An error occurred while submitting your inquiry. Please try again or contact us directly.')
            return self.get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """
        Add services data to the context with proper error handling.
        """
        context = super().get_context_data(**kwargs)
        
        try:
            # Import here to avoid circular imports
            from apps.services.models import Service, ServiceInquiry
            
            # Get all active and published services
            all_services = Service.objects.filter(
                is_active=True,
                is_published=True,
                published_at__lte=timezone.now()
            ).order_by('-order_priority', '-created_at')
            
            # Handle search query
            search_query = self.request.GET.get('search', '').strip()
            if search_query:
                all_services = all_services.filter(
                    Q(title__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(detailed_content__icontains=search_query)
                )
            
            # Handle category/type filter (if you want to add categories later)
            service_type = self.request.GET.get('type', '').strip()
            if service_type and service_type != 'all':
                # This can be extended when you add category field to Service model
                pass
            
            # Handle price range filter
            price_filter = self.request.GET.get('price', '').strip()
            if price_filter and price_filter != 'all':
                all_services = all_services.filter(price_range__icontains=price_filter)
            
            context['services'] = all_services
            context['total_services'] = all_services.count()
            
            # Get featured services (top 3 by order_priority)
            try:
                featured_services = all_services.filter(
                    order_priority__gt=0
                )[:3]
                context['featured_services'] = featured_services
                context['has_featured'] = featured_services.exists()
            except Exception as e:
                logger.error(f"Error fetching featured services: {e}")
                context['featured_services'] = Service.objects.none()
                context['has_featured'] = False
            
            # Get service statistics
            try:
                total_inquiries = ServiceInquiry.objects.count()
                new_inquiries = ServiceInquiry.objects.filter(status='new').count()
                converted_inquiries = ServiceInquiry.objects.filter(status='converted').count()
                
                context['stats'] = {
                    'total_services': all_services.count(),
                    'total_inquiries': total_inquiries,
                    'new_inquiries': new_inquiries,
                    'converted_inquiries': converted_inquiries,
                    'conversion_rate': round((converted_inquiries / total_inquiries * 100), 1) if total_inquiries > 0 else 0,
                }
            except Exception as e:
                logger.error(f"Error calculating service statistics: {e}")
                context['stats'] = {
                    'total_services': 0,
                    'total_inquiries': 0,
                    'new_inquiries': 0,
                    'converted_inquiries': 0,
                    'conversion_rate': 0,
                }
            
            # Get available price ranges for filtering
            try:
                price_ranges = all_services.exclude(
                    Q(price_range__isnull=True) | Q(price_range__exact='')
                ).values_list('price_range', flat=True).distinct()
                context['available_price_ranges'] = list(price_ranges)
                context['has_price_ranges'] = len(price_ranges) > 0
            except Exception as e:
                logger.error(f"Error fetching price ranges: {e}")
                context['available_price_ranges'] = []
                context['has_price_ranges'] = False
            
            # Add current filters for template
            context['current_filters'] = {
                'search': search_query,
                'type': service_type if service_type else 'all',
                'price': price_filter if price_filter else 'all',
            }
            
            # Add filter status
            has_active_filters = any([
                search_query,
                service_type and service_type != 'all',
                price_filter and price_filter != 'all',
            ])
            context['has_active_filters'] = has_active_filters
            
        except Exception as e:
            logger.error(f"Error building context for services page: {e}")
            # Provide safe defaults in case of major errors
            context.update({
                'services': Service.objects.none() if 'Service' in locals() else [],
                'total_services': 0,
                'featured_services': Service.objects.none() if 'Service' in locals() else [],
                'has_featured': False,
                'stats': {
                    'total_services': 0,
                    'total_inquiries': 0,
                    'new_inquiries': 0,
                    'converted_inquiries': 0,
                    'conversion_rate': 0,
                },
                'available_price_ranges': [],
                'has_price_ranges': False,
                'current_filters': {
                    'search': '',
                    'type': 'all',
                    'price': 'all',
                },
                'has_active_filters': False,
            })
        
        return context
    
    
class ContactView(FormView):
    """
    Class-based view for the contact page with form handling.
    Handles both GET requests (display form) and POST requests (process form).
    """
    template_name = 'pages/contact.html'
    form_class = ContactForm
    success_url = '/contact/'
    
    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        
        # Add any additional context if needed
        context['page_title'] = 'Contact Us'
        context['meta_description'] = 'Get in touch with Pulcova for your next software development project.'
        
        return context
    
    def form_valid(self, form):
        """
        Handle valid form submission with comprehensive error handling.
        """
        try:
            # Extract form data
            cleaned_data = form.cleaned_data
            first_name = cleaned_data.get('first_name')
            last_name = cleaned_data.get('last_name')
            email = cleaned_data.get('email')
            company = cleaned_data.get('company', 'Not specified')
            project_type = cleaned_data.get('project_type')
            budget = cleaned_data.get('budget', 'Not specified')
            timeline = cleaned_data.get('timeline', 'Not specified')
            message = cleaned_data.get('message')
            
            # Prepare email content
            full_name = f"{first_name} {last_name}"
            project_type_display = dict(form.fields['project_type'].choices).get(project_type, project_type)
            budget_display = dict(form.fields['budget'].choices).get(budget, budget)
            timeline_display = dict(form.fields['timeline'].choices).get(timeline, timeline)
            
            # Email subject
            subject = f"New Contact Form Submission from {full_name}"
            
            # Email body (HTML version)
            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px;">
                        New Contact Form Submission
                    </h2>
                    
                    <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #1e293b;">Contact Information</h3>
                        <p><strong>Name:</strong> {full_name}</p>
                        <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
                        <p><strong>Company:</strong> {company}</p>
                    </div>
                    
                    <div style="background-color: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #1e293b;">Project Details</h3>
                        <p><strong>Project Type:</strong> {project_type_display}</p>
                        <p><strong>Budget Range:</strong> {budget_display}</p>
                        <p><strong>Timeline:</strong> {timeline_display}</p>
                    </div>
                    
                    <div style="background-color: #fefce8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #1e293b;">Message</h3>
                        <p style="white-space: pre-wrap;">{message}</p>
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; font-size: 0.9em; color: #64748b;">
                        <p><strong>Submitted:</strong> {timezone.now().strftime('%B %d, %Y at %I:%M %p UTC')}</p>
                        <p><strong>Source:</strong> Pulcova Contact Form</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            plain_message = f"""
New Contact Form Submission

Contact Information:
- Name: {full_name}
- Email: {email}
- Company: {company}

Project Details:
- Project Type: {project_type_display}
- Budget Range: {budget_display}
- Timeline: {timeline_display}

Message:
{message}

Submitted: {timezone.now().strftime('%B %d, %Y at %I:%M %p UTC')}
Source: Pulcova Contact Form
            """
            
            # Send email to yourself
            try:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['hello@pulcova.store'],  # Your email
                    html_message=html_message,
                    fail_silently=False,
                )
                logger.info(f"Contact form email sent successfully for {email}")
            except BadHeaderError:
                logger.error("Invalid header found in email.")
                messages.error(self.request, 'Invalid email format. Please try again.')
                return self.form_invalid(form)
            except Exception as e:
                logger.error(f"Failed to send contact form email: {e}")
                logger.error(traceback.format_exc())
                messages.error(
                    self.request,
                    'There was an error sending your message. Please try again or contact us directly.'
                )
                return self.form_invalid(form)
            
            # Send confirmation email to the user
            try:
                confirmation_subject = "Thank you for contacting Pulcova!"
                confirmation_html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2563eb;">Thank you for reaching out!</h2>
                        
                        <p>Hi {first_name},</p>
                        
                        <p>Thank you for contacting Pulcova! I've received your message about your <strong>{project_type_display.lower()}</strong> project and will get back to you within 24 hours.</p>
                        
                        <div style="background-color: #f8fafc; padding: 15px; border-left: 4px solid #2563eb; margin: 20px 0;">
                            <p style="margin: 0;"><strong>What's next?</strong></p>
                            <ul style="margin: 10px 0 0 0;">
                                <li>I'll review your project requirements</li>
                                <li>Prepare a detailed response with next steps</li>
                                <li>Reach out to schedule a consultation if needed</li>
                            </ul>
                        </div>
                        
                        <p>In the meantime, feel free to check out my <a href="https://pulcova.store/portfolio" style="color: #2563eb;">portfolio</a> and <a href="https://pulcova.store/blog" style="color: #2563eb;">blog</a> for more information about my work.</p>
                        
                        <p>Best regards,<br>
                        <strong>Pulcova</strong><br>
                        Full Stack Software Engineer</p>
                        
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; font-size: 0.9em; color: #64748b;">
                            <p>This is an automated confirmation. Please don't reply to this email.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                confirmation_plain = f"""
Hi {first_name},

Thank you for contacting Pulcova! I've received your message about your {project_type_display.lower()} project and will get back to you within 24 hours.

What's next?
- I'll review your project requirements
- Prepare a detailed response with next steps
- Reach out to schedule a consultation if needed

In the meantime, feel free to check out my portfolio and blog for more information about my work.

Best regards,
Pulcova
Full Stack Software Engineer

This is an automated confirmation. Please don't reply to this email.
                """
                
                send_mail(
                    subject=confirmation_subject,
                    message=confirmation_plain,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=confirmation_html,
                    fail_silently=True,  # Don't fail if confirmation email fails
                )
                logger.info(f"Confirmation email sent to {email}")
            except Exception as e:
                # Log error but don't fail the form submission
                logger.warning(f"Failed to send confirmation email to {email}: {e}")
            
            # Add success message
            messages.success(
                self.request,
                f"Thank you, {first_name}! Your message has been sent successfully. "
                f"I'll get back to you within 24 hours."
            )
            
            # Log successful submission
            logger.info(f"Contact form submitted successfully by {email} - {full_name}")
            
            # Handle AJAX requests
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f"Thank you, {first_name}! Your message has been sent successfully."
                })
            
            return super().form_valid(form)
            
        except Exception as e:
            # Log the full error for debugging
            logger.error(f"Unexpected error in contact form submission: {e}")
            logger.error(traceback.format_exc())
            
            # Add error message
            messages.error(
                self.request,
                'An unexpected error occurred. Please try again or contact us directly.'
            )
            
            # Handle AJAX requests
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'An error occurred. Please try again.'
                })
            
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """
        Handle invalid form submission.
        """
        logger.warning(f"Contact form submission failed validation: {form.errors}")
        
        # Add error message
        messages.error(
            self.request,
            'Please correct the errors below and try again.'
        )
        
        # Handle AJAX requests
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors and try again.',
                'errors': form.errors
            })
        
        return super().form_invalid(form)