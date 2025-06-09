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
