from django import forms
from django.core.exceptions import ValidationError
from .models import Newsletter


class NewsletterSubscriptionForm(forms.ModelForm):
    """
    Form for newsletter subscription
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'flex-1 px-4 py-2 rounded-lg border border-primary-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-white',
            'placeholder': 'Enter your email',
            'required': True,
        }),
        error_messages={
            'required': 'Please enter your email address.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    
    class Meta:
        model = Newsletter
        fields = ['email']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists and is active
            existing_subscription = Newsletter.objects.filter(
                email=email, 
                is_active=True
            ).first()
            
            if existing_subscription:
                raise ValidationError(
                    "This email is already subscribed to our newsletter."
                )
            
            # Reactivate if exists but inactive
            inactive_subscription = Newsletter.objects.filter(
                email=email, 
                is_active=False
            ).first()
            
            if inactive_subscription:
                # We'll handle reactivation in the view
                pass
                
        return email


class NewsletterUnsubscribeForm(forms.Form):
    """
    Form for newsletter unsubscription
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500',
            'placeholder': 'Enter your email to unsubscribe',
            'required': True,
        }),
        error_messages={
            'required': 'Please enter your email address.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email exists and is active
            subscription = Newsletter.objects.filter(
                email=email, 
                is_active=True
            ).first()
            
            if not subscription:
                raise ValidationError(
                    "This email is not found in our newsletter subscriptions."
                )
                
        return email
