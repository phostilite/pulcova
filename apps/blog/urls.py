from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Blog list view
    path('', views.ArticleListView.as_view(), name='article_list'),
    
    # Blog detail view
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
]