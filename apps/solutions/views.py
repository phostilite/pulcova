from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from django.http import Http404
from django.core.exceptions import ValidationError
from django.db.models import F
from django.utils import timezone
from django.db import transaction
import logging

from .models import Solution, CodeSnippet
from apps.portfolio.models import Technology
from apps.blog.models import Tag

logger = logging.getLogger(__name__)


class SolutionDetailView(DetailView):
    """
    Class-based view for displaying individual solution details.
    Handles error cases, null values, view counting, and database optimization.
    """
    model = Solution
    template_name = 'solutions/solution_detail.html'
    context_object_name = 'solution'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """
        Return the queryset with optimized database queries and published filter.
        """
        return Solution.objects.select_related(
            'technology'
        ).prefetch_related(
            'related_solutions__technology',
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
        
        # Get the solution slug from URL
        slug = self.kwargs.get(self.slug_url_kwarg)
        if not slug:
            logger.error("No slug provided in URL for SolutionDetailView")
            raise Http404("Solution not found")
        
        try:
            # Validate slug format
            if not slug.replace('-', '').replace('_', '').isalnum():
                logger.warning(f"Invalid slug format: {slug}")
                raise Http404("Invalid solution identifier")
            
            # Get the solution object
            solution = get_object_or_404(queryset, **{self.slug_field: slug})
            
            # Safely increment view count using atomic database operation
            # This prevents race conditions when multiple users view simultaneously
            try:
                with transaction.atomic():
                    Solution.objects.filter(pk=solution.pk).update(
                        view_count=F('view_count') + 1
                    )
                    # Refresh the object to get updated view_count
                    solution.refresh_from_db(fields=['view_count'])
                    
            except Exception as e:
                # Log the error but don't fail the request if view count update fails
                logger.warning(f"Failed to increment view count for solution {solution.slug}: {e}")
            
            return solution
            
        except Http404:
            logger.info(f"Solution with slug '{slug}' not found or not published")
            raise
        except ValidationError as e:
            logger.error(f"Validation error when retrieving solution: {e}")
            raise Http404("Invalid solution identifier")
        except Exception as e:
            logger.error(f"Unexpected error retrieving solution with slug '{slug}': {e}")
            raise Http404("Solution not found")
    
    def get_context_data(self, **kwargs):
        """
        Add additional context data with proper error handling for optional fields.
        """
        context = super().get_context_data(**kwargs)
        solution = self.object
        
        try:
            # Handle technology information safely
            try:
                context['technology_info'] = self.get_technology_info(solution)
                context['has_technology'] = solution.technology is not None
            except Exception as e:
                logger.error(f"Error fetching technology info for solution {solution.slug}: {e}")
                context['technology_info'] = None
                context['has_technology'] = False
            
            # Handle related solutions with error handling
            try:
                related_solutions = self.get_related_solutions(solution)
                context['related_solutions'] = related_solutions
                context['has_related_solutions'] = related_solutions.exists()
                context['related_solutions_count'] = related_solutions.count()
            except Exception as e:
                logger.error(f"Error fetching related solutions for solution {solution.slug}: {e}")
                context['related_solutions'] = Solution.objects.none()
                context['has_related_solutions'] = False
                context['related_solutions_count'] = 0
            
            # Handle code snippets related to this solution's technology
            try:
                code_snippets = self.get_related_code_snippets(solution)
                context['code_snippets'] = code_snippets
                context['has_code_snippets'] = code_snippets.exists()
                context['code_snippets_count'] = code_snippets.count()
            except Exception as e:
                logger.error(f"Error fetching code snippets for solution {solution.slug}: {e}")
                context['code_snippets'] = CodeSnippet.objects.none()
                context['has_code_snippets'] = False
                context['code_snippets_count'] = 0
            
            # Handle difficulty level display
            context['difficulty_display'] = solution.get_difficulty_level_display()
            context['difficulty_class'] = self.get_difficulty_css_class(solution.difficulty_level)
            
            # Handle view count and helpful count with fallbacks
            context['view_count'] = getattr(solution, 'view_count', 0)
            context['helpful_count'] = getattr(solution, 'helpful_count', 0)
            
            # Add breadcrumb data
            context['breadcrumbs'] = [
                {'title': 'Home', 'url': '/', 'current': False},
                {'title': 'Solutions', 'url': '/solutions/', 'current': False},
                {'title': solution.title, 'url': solution.get_absolute_url(), 'current': True}
            ]
            
            # Add schema.org structured data for SEO
            context['structured_data'] = self.get_structured_data(solution)
            
        except Exception as e:
            logger.error(f"Error building context for solution {solution.id}: {e}")
            # Continue with basic context even if additional data fails
            
        return context
    
    def get_technology_info(self, solution):
        """
        Safely get technology information with null handling.
        """
        try:
            if not solution.technology:
                return None
            
            technology = solution.technology
            return {
                'name': getattr(technology, 'name', 'Unknown'),
                'slug': getattr(technology, 'slug', ''),
                'category': getattr(technology, 'get_category_display', lambda: 'Other')(),
                'icon': technology.icon if hasattr(technology, 'icon') and technology.icon else None
            }
        except Exception as e:
            logger.error(f"Error getting technology info: {e}")
            return None
    
    def get_related_solutions(self, solution):
        """
        Get related solutions with proper error handling.
        """
        try:
            # Get solutions with the same technology, excluding current solution
            related = Solution.objects.select_related('technology').filter(
                technology=solution.technology,
                is_published=True,
                published_at__lte=timezone.now()
            ).exclude(
                id=solution.id
            ).order_by('-helpful_count', '-created_at')
            
            # Also include manually related solutions
            if solution.related_solutions.exists():
                manual_related = solution.related_solutions.filter(
                    is_published=True,
                    published_at__lte=timezone.now()
                ).exclude(
                    id=solution.id
                ).select_related('technology')
                
                # Combine and deduplicate
                related = (related | manual_related).distinct()
            
            return related[:6]  # Limit to 6 related solutions
            
        except Exception as e:
            logger.error(f"Error fetching related solutions: {e}")
            return Solution.objects.none()
    
    def get_related_code_snippets(self, solution):
        """
        Get code snippets related to this solution's technology.
        """
        try:
            if not solution.technology:
                return CodeSnippet.objects.none()
            
            # Find code snippets that might be related by technology name
            snippets = CodeSnippet.objects.filter(
                language__icontains=solution.technology.name.lower()
            ).order_by('-created_at')
            
            # If no direct language match, try to find by tags
            if not snippets.exists():
                snippets = CodeSnippet.objects.filter(
                    tags__name__icontains=solution.technology.name
                ).distinct().order_by('-created_at')
            
            return snippets[:3]  # Limit to 3 code snippets
            
        except Exception as e:
            logger.error(f"Error fetching related code snippets: {e}")
            return CodeSnippet.objects.none()
    
    def get_difficulty_css_class(self, difficulty_level):
        """
        Return CSS class for difficulty level styling.
        """
        difficulty_classes = {
            'beginner': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
            'intermediate': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
            'advanced': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
        }
        return difficulty_classes.get(difficulty_level, 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300')
    
    def get_structured_data(self, solution):
        """
        Generate structured data for SEO.
        """
        try:
            return {
                '@context': 'https://schema.org',
                '@type': 'TechArticle',
                'headline': solution.title,
                'description': solution.problem_description[:160],
                'author': {
                    '@type': 'Person',
                    'name': 'Pulcova'
                },
                'datePublished': solution.published_at.isoformat() if solution.published_at else solution.created_at.isoformat(),
                'dateModified': solution.updated_at.isoformat(),
                'mainEntityOfPage': {
                    '@type': 'WebPage',
                    '@id': solution.get_absolute_url()
                },
                'proficiencyLevel': solution.get_difficulty_level_display(),
                'about': solution.technology.name if solution.technology else 'Programming'
            }
        except Exception as e:
            logger.error(f"Error generating structured data: {e}")
            return {}


# Create your views here.
