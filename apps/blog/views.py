from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DetailView, ListView, View
from django.http import Http404, JsonResponse
from django.core.exceptions import ValidationError
from django.db.models import F, Q
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
import logging
import json

from .models import Article, Category, Tag, Newsletter
from .forms import NewsletterSubscriptionForm, NewsletterUnsubscribeForm

logger = logging.getLogger(__name__)


class ArticleDetailView(DetailView):
    """
    Class-based view for displaying individual blog articles.
    Handles error cases, null values, and view counting.
    """
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'
    slug_field = 'slug'  # Assuming you have a slug field in your SEOModel
    slug_url_kwarg = 'slug'
    
    def get_object(self, queryset=None):
        """
        Override get_object to add custom error handling and view counting.
        """
        try:
            # Get the base queryset
            if queryset is None:
                queryset = self.get_queryset()
            
            # Get the slug from URL
            slug = self.kwargs.get(self.slug_url_kwarg)
            if not slug:
                logger.error("No slug provided in URL")
                raise Http404("Article slug is required")
            
            # Try to get the article
            try:
                article = queryset.get(**{self.slug_field: slug})
            except Article.DoesNotExist:
                logger.warning(f"Article with slug '{slug}' not found")
                raise Http404("Article not found")
            except Article.MultipleObjectsReturned:
                logger.error(f"Multiple articles found with slug '{slug}'")
                # Get the most recent one
                article = queryset.filter(**{self.slug_field: slug}).first()
            
            # Check if article is published (if it has publish status)
            if hasattr(article, 'is_published') and not article.is_published:
                logger.warning(f"Attempted access to unpublished article: {slug}")
                raise Http404("Article not found")
            
            # Check if article has future publish date
            if hasattr(article, 'published_at') and article.published_at:
                if article.published_at > timezone.now():
                    logger.warning(f"Attempted access to future article: {slug}")
                    raise Http404("Article not found")
            
            return article
            
        except ValidationError as e:
            logger.error(f"Validation error when retrieving article: {e}")
            raise Http404("Invalid article identifier")
        except Exception as e:
            logger.error(f"Unexpected error when retrieving article: {e}")
            raise Http404("Article could not be retrieved")
    
    def get_queryset(self):
        """
        Override queryset to include related objects and optimize queries.
        """
        return Article.objects.select_related(
            'author', 
            'category'
        ).prefetch_related(
            'tags',
            'category__subcategories'
        ).filter(
            # Add any additional filters here if needed
        )
    
    def get_context_data(self, **kwargs):
        """
        Add additional context data with null value handling.
        """
        context = super().get_context_data(**kwargs)
        article = self.object
        
        try:
            # Safely get related articles with null handling
            context['related_articles'] = self.get_related_articles(article)
            
            # Safely get category information
            context['category_info'] = self.get_category_info(article)
            
            # Safely get author information
            context['author_info'] = self.get_author_info(article)
            
            # Safely get tags
            context['article_tags'] = self.get_article_tags(article)
            
            # Add reading time with fallback
            context['reading_time'] = getattr(article, 'reading_time', 5)
            
            # Add view count with fallback
            context['view_count'] = getattr(article, 'view_count', 0)
            
        except Exception as e:
            logger.error(f"Error building context for article {article.id}: {e}")
            # Continue with basic context even if additional data fails
            
        return context
    
    def get_related_articles(self, article):
        """
        Get related articles with proper error handling.
        """
        try:
            if not article.category:
                return Article.objects.none()
            
            related = Article.objects.select_related('author', 'category').filter(
                category=article.category
            ).exclude(
                id=article.id
            )
            
            # Add published filter if applicable
            if hasattr(Article, 'is_published'):
                related = related.filter(is_published=True)
            
            return related[:4]  # Limit to 4 related articles
            
        except Exception as e:
            logger.error(f"Error fetching related articles: {e}")
            return Article.objects.none()
    
    def get_category_info(self, article):
        """
        Safely get category information with null handling.
        """
        try:
            if not article.category:
                return None
            
            category = article.category
            return {
                'name': getattr(category, 'name', 'Uncategorized'),
                'slug': getattr(category, 'slug', ''),
                'description': getattr(category, 'description', ''),
                'parent': getattr(category, 'parent', None)
            }
        except Exception as e:
            logger.error(f"Error getting category info: {e}")
            return None
    
    def get_author_info(self, article):
        """
        Safely get author information with null handling.
        """
        try:
            if not article.author:
                return None
            
            author = article.author
            return {
                'username': getattr(author, 'username', 'Anonymous'),
                'first_name': getattr(author, 'first_name', ''),
                'last_name': getattr(author, 'last_name', ''),
                'email': getattr(author, 'email', ''),
                'full_name': f"{getattr(author, 'first_name', '')} {getattr(author, 'last_name', '')}".strip() or getattr(author, 'username', 'Anonymous')
            }
        except Exception as e:
            logger.error(f"Error getting author info: {e}")
            return None
    
    def get_article_tags(self, article):
        """
        Safely get article tags with null handling.
        """
        try:
            return article.tags.all() if hasattr(article, 'tags') else []
        except Exception as e:
            logger.error(f"Error getting article tags: {e}")
            return []
    
    def get(self, request, *args, **kwargs):
        """
        Override get method to increment view count safely.
        """
        try:
            # Get the object first
            self.object = self.get_object()
            
            # Increment view count atomically
            try:
                Article.objects.filter(id=self.object.id).update(
                    view_count=F('view_count') + 1
                )
                # Refresh the object to get updated view count
                self.object.refresh_from_db(fields=['view_count'])
            except Exception as e:
                logger.warning(f"Failed to increment view count for article {self.object.id}: {e}")
                # Continue without incrementing view count
            
            # Get context and render
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
            
        except Http404:
            # Re-raise 404 errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error in ArticleDetailView: {e}")
            # Return a generic error page or 404
            raise Http404("Article could not be displayed")


class ArticleListView(ListView):
    """
    Class-based view for listing blog articles with pagination and filtering.
    """
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 12
    ordering = ['-published_at', '-created_at']
    
    def get_queryset(self):
        """
        Override queryset to only show published articles and optimize queries.
        """
        queryset = Article.objects.select_related(
            'author', 
            'category'
        ).prefetch_related(
            'tags'
        ).filter(
            is_published=True,
            published_at__lte=timezone.now()
        )
        
        # Handle search
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        
        # Handle category filter
        category_slug = self.request.GET.get('category', '').strip()
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug)
                queryset = queryset.filter(category=category)
            except Category.DoesNotExist:
                logger.warning(f"Category with slug '{category_slug}' not found")
        
        # Handle tag filter
        tag_slug = self.request.GET.get('tag', '').strip()
        if tag_slug:
            try:
                tag = Tag.objects.get(slug=tag_slug)
                queryset = queryset.filter(tags=tag)
            except Tag.DoesNotExist:
                logger.warning(f"Tag with slug '{tag_slug}' not found")
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Add additional context for the article list.
        """
        context = super().get_context_data(**kwargs)
        
        try:
            # Add categories for filter
            context['categories'] = Category.objects.filter(
                articles__is_published=True
            ).distinct().order_by('name')
            
            # Add popular tags
            context['popular_tags'] = Tag.objects.filter(
                article__is_published=True
            ).distinct().order_by('name')[:20]
            
            # Add featured articles
            context['featured_articles'] = Article.objects.filter(
                is_published=True,
                is_featured=True,
                published_at__lte=timezone.now()
            ).select_related('author', 'category')[:3]
            
            # Add current filters to context
            context['current_search'] = self.request.GET.get('search', '')
            context['current_category'] = self.request.GET.get('category', '')
            context['current_tag'] = self.request.GET.get('tag', '')
            
        except Exception as e:
            logger.error(f"Error building context for article list: {e}")
        
        return context


class NewsletterSubscriptionView(View):
    """
    Handle newsletter subscription via AJAX or regular POST
    """
    
    def post(self, request, *args, **kwargs):
        form = NewsletterSubscriptionForm(request.POST)
        
        # Check if it's an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                # Check if email exists but is inactive
                existing_subscription = Newsletter.objects.filter(email=email).first()
                
                if existing_subscription:
                    if existing_subscription.is_active:
                        message = "You're already subscribed to our newsletter!"
                        status = 'warning'
                    else:
                        # Reactivate subscription
                        existing_subscription.is_active = True
                        existing_subscription.save()
                        message = "Welcome back! Your subscription has been reactivated."
                        status = 'success'
                else:
                    # Create new subscription
                    subscription = form.save(commit=False)
                    subscription.source = request.GET.get('source', 'blog')
                    subscription.save()
                    message = "Successfully subscribed to our newsletter!"
                    status = 'success'
                    
                    # Send welcome email (optional)
                    try:
                        self.send_welcome_email(email)
                    except Exception as e:
                        logger.error(f"Failed to send welcome email to {email}: {e}")
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': message,
                        'status': status
                    })
                else:
                    messages.success(request, message)
                    return redirect(request.META.get('HTTP_REFERER', '/blog/'))
                    
            except Exception as e:
                logger.error(f"Error processing newsletter subscription: {e}")
                error_message = "An error occurred. Please try again later."
                
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': error_message,
                        'status': 'error'
                    })
                else:
                    messages.error(request, error_message)
                    return redirect(request.META.get('HTTP_REFERER', '/blog/'))
        else:
            # Form has errors
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(error)
            
            error_message = '; '.join(error_messages) if error_messages else "Please check your input."
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message,
                    'status': 'error',
                    'errors': form.errors
                })
            else:
                messages.error(request, error_message)
                return redirect(request.META.get('HTTP_REFERER', '/blog/'))
    
    def send_welcome_email(self, email):
        """
        Send welcome email to new subscriber
        """
        try:
            subject = "Welcome to Pulcova Newsletter!"
            message = f"""
            Hi there!
            
            Thank you for subscribing to the Pulcova newsletter! 🎉
            
            You'll now receive:
            • Latest technical articles and tutorials
            • Software development insights and best practices
            • Updates on new projects and solutions
            • Exclusive content and early access to new posts
            
            If you ever want to unsubscribe, you can do so at: {settings.SITE_URL}/blog/newsletter/unsubscribe/
            
            Best regards,
            Pulcova Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@pulcova.com'),
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
            raise


class NewsletterUnsubscribeView(View):
    """
    Handle newsletter unsubscription
    """
    template_name = 'blog/newsletter_unsubscribe.html'
    
    def get(self, request, token=None):
        context = {'form': NewsletterUnsubscribeForm()}
        
        # Handle token-based unsubscribe
        if token:
            try:
                subscription = Newsletter.objects.get(
                    unsubscribe_token=token,
                    is_active=True
                )
                subscription.is_active = False
                subscription.save()
                
                messages.success(request, "You have been successfully unsubscribed from our newsletter.")
                context['unsubscribed'] = True
                
            except Newsletter.DoesNotExist:
                messages.error(request, "Invalid unsubscribe link or you're already unsubscribed.")
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = NewsletterUnsubscribeForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                subscription = Newsletter.objects.get(
                    email=email,
                    is_active=True
                )
                subscription.is_active = False
                subscription.save()
                
                messages.success(request, "You have been successfully unsubscribed from our newsletter.")
                
                # Send confirmation email
                try:
                    self.send_unsubscribe_confirmation(email)
                except Exception as e:
                    logger.error(f"Failed to send unsubscribe confirmation to {email}: {e}")
                
            except Newsletter.DoesNotExist:
                messages.error(request, "This email is not found in our newsletter subscriptions.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
        
        return render(request, self.template_name, {'form': form})
    
    def send_unsubscribe_confirmation(self, email):
        """
        Send unsubscribe confirmation email
        """
        try:
            subject = "Unsubscribed from Pulcova Newsletter"
            message = f"""
            Hi there,
            
            You have been successfully unsubscribed from the Pulcova newsletter.
            
            If this was done by mistake, you can resubscribe at: {settings.SITE_URL}/blog/
            
            Thank you for your time with us!
            
            Best regards,
            Pulcova Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@pulcova.com'),
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send unsubscribe confirmation: {e}")
            raise