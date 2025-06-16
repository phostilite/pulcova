from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Blog list view
    path('', views.ArticleListView.as_view(), name='article_list'),
    
    # Newsletter subscription
    path('newsletter/subscribe/', views.NewsletterSubscriptionView.as_view(), name='newsletter_subscribe'),
    
    # Newsletter unsubscription
    path('newsletter/unsubscribe/', views.NewsletterUnsubscribeView.as_view(), name='newsletter_unsubscribe'),
    path('newsletter/unsubscribe/<str:token>/', views.NewsletterUnsubscribeView.as_view(), name='newsletter_unsubscribe_token'),
    
    # Blog detail view (keep this last to avoid conflicts)
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
]