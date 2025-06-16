from django.urls import path
from . import views

app_name = 'solutions'

urlpatterns = [
    path('<slug:slug>/', views.SolutionDetailView.as_view(), name='solution_detail'),
]