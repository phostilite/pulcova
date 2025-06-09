from django.views.generic import TemplateView


class PrivacyPolicyView(TemplateView):
    """
    Class-based view for the privacy policy page.
    """
    template_name = 'legal/privacy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Privacy Policy'
        context['last_updated'] = '2025-06-09'
        return context


class TermsConditionsView(TemplateView):
    """
    Class-based view for the terms and conditions page.
    """
    template_name = 'legal/terms.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Terms & Conditions'
        context['last_updated'] = '2025-06-09'
        return context


class CookiePolicyView(TemplateView):
    """
    Class-based view for the cookie policy page.
    """
    template_name = 'legal/cookies.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Cookie Policy'
        context['last_updated'] = '2025-06-09'
        return context


class GDPRNoticeView(TemplateView):
    """
    Class-based view for the GDPR notice page.
    """
    template_name = 'legal/gdpr.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'GDPR Notice'
        context['last_updated'] = '2025-06-09'
        return context


class RefundPolicyView(TemplateView):
    """
    Class-based view for the refund policy page.
    """
    template_name = 'legal/refund.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Refund Policy'
        context['last_updated'] = '2025-06-09'
        return context
