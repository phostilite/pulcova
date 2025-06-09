from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from .models import Article

# Create your views here.

class ArticleListView(ListView):
    """List view for blog articles"""
    model = Article
    template_name = 'pages/blog.html'  # Using existing blog template
    context_object_name = 'articles'
    queryset = Article.objects.filter(is_published=True)
    paginate_by = 12

class ArticleDetailView(DetailView):
    """Detail view for individual blog articles"""
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'
    queryset = Article.objects.filter(is_published=True)
