from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from .models import Project

# Create your views here.

class ProjectListView(ListView):
    """List view for portfolio projects"""
    model = Project
    template_name = 'pages/portfolio.html'  # Using existing portfolio template
    context_object_name = 'projects'
    queryset = Project.objects.filter(is_published=True)
    paginate_by = 12

class ProjectDetailView(DetailView):
    """Detail view for individual portfolio projects"""
    model = Project
    template_name = 'portfolio/project_detail.html'
    context_object_name = 'project'
    queryset = Project.objects.filter(is_published=True)
