from django.views.generic import TemplateView


class HomeView(TemplateView):
    """
    Class-based view for the home page.
    """
    template_name = 'pages/home.html'
    
    
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