# filepath: /home/priyanshu-sharma/Documents/pulcova/apps/pages/urls.py
from django.urls import path
from .views import HomeView

app_name = 'pages'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]