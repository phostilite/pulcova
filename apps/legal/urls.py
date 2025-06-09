from django.urls import path
from .views import (
    PrivacyPolicyView, 
    TermsConditionsView, 
    CookiePolicyView, 
    GDPRNoticeView, 
    RefundPolicyView
)

app_name = 'legal'

urlpatterns = [
    path('privacy/', PrivacyPolicyView.as_view(), name='privacy'),
    path('terms/', TermsConditionsView.as_view(), name='terms'),
    path('cookies/', CookiePolicyView.as_view(), name='cookies'),
    path('gdpr/', GDPRNoticeView.as_view(), name='gdpr'),
    path('refund/', RefundPolicyView.as_view(), name='refund'),
]
