# filepath: /home/priyanshu-sharma/Documents/pulcova/apps/pages/urls.py
from django.urls import path
from .views import HomeView, AboutView, PortfolioView, BlogView, SolutionsView

app_name = 'pages'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('portfolio/', PortfolioView.as_view(), name='portfolio'),
    path('blog/', BlogView.as_view(), name='blog'),
    path('solutions/', SolutionsView.as_view(), name='solutions'),
]