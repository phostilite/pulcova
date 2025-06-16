from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # API endpoints
    path('lead/', views.save_chatbot_lead, name='save_lead'),
    path('conversation/', views.save_conversation, name='save_conversation'),
]