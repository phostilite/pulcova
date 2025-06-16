from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.http import Http404
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Project, Technology, GalleryImage
import logging

logger = logging.getLogger(__name__)


class ProjectListView(ListView):
    """List view for portfolio projects"""
    model = Project
    template_name = 'pages/portfolio.html'
    context_object_name = 'projects'
    queryset = Project.objects.filter(is_published=True)
    paginate_by = 12


class ProjectDetailView(DetailView):
    """
    Detail view for individual portfolio projects with comprehensive error handling
    and optimized database queries.
    """
    model = Project
    template_name = 'portfolio/project_detail.html'
    context_object_name = 'project'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """
        Return the queryset with optimized database queries and published filter.
        """
        return Project.objects.select_related().prefetch_related(
            'tech_stack',
            'gallery_images'
        ).filter(
            is_published=True,
            published_at__lte=timezone.now()
        )
    
    def get_object(self, queryset=None):
        """
        Override get_object to add comprehensive error handling and view count increment.
        """
        if queryset is None:
            queryset = self.get_queryset()
        
        # Get the project slug from URL
        slug = self.kwargs.get(self.slug_url_kwarg)
        if not slug:
            logger.error("No slug provided in URL for ProjectDetailView")
            raise Http404("Project not found")
        
        try:
            # Get the project object
            project = get_object_or_404(queryset, **{self.slug_field: slug})
            
            # Safely increment view count using atomic database operation
            # This prevents race conditions when multiple users view simultaneously
            try:
                with transaction.atomic():
                    Project.objects.filter(pk=project.pk).update(
                        view_count=F('view_count') + 1
                    )
                    # Refresh the object to get updated view_count
                    project.refresh_from_db(fields=['view_count'])
                    
            except Exception as e:
                # Log the error but don't fail the request if view count update fails
                logger.warning(f"Failed to increment view count for project {project.slug}: {e}")
            
            return project
            
        except Http404:
            logger.info(f"Project with slug '{slug}' not found or not published")
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving project with slug '{slug}': {e}")
            raise Http404("Project not found")
    
    def get_context_data(self, **kwargs):
        """
        Add additional context data with proper error handling for optional fields.
        """
        context = super().get_context_data(**kwargs)
        project = self.object
        
        try:
            # Handle tech stack with error handling
            try:
                tech_stack = project.tech_stack.all().order_by('category', 'name')
                # Group technologies by category for better template organization
                tech_by_category = {}
                for tech in tech_stack:
                    category = tech.get_category_display()
                    if category not in tech_by_category:
                        tech_by_category[category] = []
                    tech_by_category[category].append(tech)
                
                context['tech_stack'] = tech_stack
                context['tech_by_category'] = tech_by_category
                context['has_tech_stack'] = tech_stack.exists()
                
            except Exception as e:
                logger.error(f"Error fetching tech stack for project {project.slug}: {e}")
                context['tech_stack'] = Technology.objects.none()
                context['tech_by_category'] = {}
                context['has_tech_stack'] = False
            
            # Handle gallery images with error handling - filter out images without files
            try:
                gallery_images = project.gallery_images.exclude(image='').filter(image__isnull=False).order_by('created_at')
                context['gallery_images'] = gallery_images
                context['has_gallery'] = gallery_images.exists()
                context['gallery_count'] = gallery_images.count()
                
            except Exception as e:
                logger.error(f"Error fetching gallery images for project {project.slug}: {e}")
                context['gallery_images'] = GalleryImage.objects.none()
                context['has_gallery'] = False
                context['gallery_count'] = 0
            
            # Handle project URLs safely
            context['has_live_url'] = bool(project.live_url and project.live_url.strip())
            context['has_github_url'] = bool(project.github_url and project.github_url.strip())
            
            # Handle project timeline
            context['has_end_date'] = project.end_date is not None
            if project.end_date:
                duration = project.end_date - project.start_date
                context['project_duration_days'] = duration.days
                context['is_ongoing'] = False
            else:
                context['is_ongoing'] = True
                if project.start_date:
                    duration = timezone.now().date() - project.start_date
                    context['project_duration_days'] = duration.days
                else:
                    context['project_duration_days'] = 0
                    
            # Add formatted duration string
            if context['project_duration_days'] > 0:
                days = context['project_duration_days']
                if days < 30:
                    context['duration_display'] = f"{days} day{'s' if days != 1 else ''}"
                elif days < 365:
                    months = round(days / 30)
                    context['duration_display'] = f"{months} month{'s' if months != 1 else ''}"
                else:
                    years = round(days / 365, 1)
                    if years == int(years):
                        years = int(years)
                    context['duration_display'] = f"{years} year{'s' if years != 1 else ''}"
                    
                if context['is_ongoing']:
                    context['duration_display'] += " (ongoing)"
            else:
                context['duration_display'] = ""
            
            # Handle featured image safely
            context['has_featured_image'] = bool(project.featured_image and hasattr(project.featured_image, 'url'))
            
            # Get related projects (same type, excluding current project)
            try:
                related_projects = Project.objects.filter(
                    is_published=True,
                    published_at__lte=timezone.now(),
                    project_type=project.project_type
                ).exclude(
                    pk=project.pk
                ).select_related().order_by('-is_featured', '-created_at')[:3]
                
                context['related_projects'] = related_projects
                context['has_related_projects'] = related_projects.exists()
                
            except Exception as e:
                logger.error(f"Error fetching related projects for {project.slug}: {e}")
                context['related_projects'] = Project.objects.none()
                context['has_related_projects'] = False
            
            # Add project type display name
            context['project_type_display'] = project.get_project_type_display()
            
            # Add breadcrumb data
            context['breadcrumbs'] = [
                {'title': 'Home', 'url': '/'},
                {'title': 'Portfolio', 'url': '/portfolio/'},
                {'title': project.title, 'url': project.get_absolute_url(), 'current': True}
            ]
            
            # Add schema.org structured data for SEO
            context['structured_data'] = {
                '@context': 'https://schema.org',
                '@type': 'CreativeWork',
                'name': project.title,
                'description': project.description,
                'url': self.request.build_absolute_uri(project.get_absolute_url()),
                'dateCreated': project.start_date.isoformat() if project.start_date else None,
                'dateModified': project.updated_at.isoformat(),
                'author': {
                    '@type': 'Person',
                    'name': 'Priyanshu Sharma'  # You can make this dynamic
                },
                'keywords': [tech.name for tech in context['tech_stack']] if context['has_tech_stack'] else []
            }
            
            # Add canonical URL for SEO
            context['canonical_url'] = self.request.build_absolute_uri(project.get_absolute_url())
            
        except Exception as e:
            logger.error(f"Error building context for project detail view {project.slug}: {e}")
            # Provide safe defaults for critical context variables
            context.update({
                'tech_stack': Technology.objects.none(),
                'tech_by_category': {},
                'has_tech_stack': False,
                'gallery_images': GalleryImage.objects.none(),
                'has_gallery': False,
                'gallery_count': 0,
                'has_live_url': False,
                'has_github_url': False,
                'has_end_date': False,
                'is_ongoing': True,
                'project_duration_days': 0,
                'has_featured_image': False,
                'related_projects': Project.objects.none(),
                'has_related_projects': False,
                'project_type_display': 'Project',
                'breadcrumbs': [
                    {'title': 'Home', 'url': '/'},
                    {'title': 'Portfolio', 'url': '/portfolio/'},
                    {'title': 'Project', 'url': '#', 'current': True}
                ]
            })
        
        return context
    
    def handle_no_permission(self):
        """
        Handle cases where user doesn't have permission to view the project.
        """
        raise Http404("Project not found")
    
    def get(self, request, *args, **kwargs):
        """
        Override get method to add additional error handling.
        """
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            # Log the 404 for monitoring
            slug = kwargs.get('slug', 'unknown')
            logger.info(f"404 error for project slug: {slug} from IP: {request.META.get('REMOTE_ADDR')}")
            raise
        except Exception as e:
            # Log unexpected errors
            slug = kwargs.get('slug', 'unknown')
            logger.error(f"Unexpected error in ProjectDetailView for slug {slug}: {e}")
            raise Http404("Project not found")