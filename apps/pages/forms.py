"""
Contact form for the pages app.
"""
from django import forms
from django.core.exceptions import ValidationError
import re


class ContactForm(forms.Form):
    """
    Contact form with comprehensive validation and security features.
    """
    
    # Form fields
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400',
            'placeholder': 'John',
            'required': True,
        }),
        error_messages={
            'required': 'First name is required.',
            'max_length': 'First name must be less than 50 characters.',
        }
    )
    
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400',
            'placeholder': 'Doe',
            'required': True,
        }),
        error_messages={
            'required': 'Last name is required.',
            'max_length': 'Last name must be less than 50 characters.',
        }
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400',
            'placeholder': 'john@example.com',
            'required': True,
        }),
        error_messages={
            'required': 'Email address is required.',
            'invalid': 'Please enter a valid email address.',
        }
    )
    
    company = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400',
            'placeholder': 'Your Company',
        })
    )
    
    PROJECT_TYPE_CHOICES = [
        ('', 'Select a project type'),
        ('web-development', 'Web Development'),
        ('api-integration', 'API Integration'),
        ('ai-ml-solutions', 'AI/ML Solutions'),
        ('mobile-app', 'Mobile Application'),
        ('e-commerce', 'E-commerce Platform'),
        ('consulting', 'Technical Consulting'),
        ('maintenance', 'Maintenance & Support'),
        ('other', 'Other'),
    ]
    
    project_type = forms.ChoiceField(
        choices=PROJECT_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white',
            'required': True,
        }),
        error_messages={
            'required': 'Please select a project type.',
        }
    )
    
    BUDGET_CHOICES = [
        ('', 'Select your budget range'),
        ('under-5k', 'Under $5,000'),
        ('5k-10k', '$5,000 - $10,000'),
        ('10k-25k', '$10,000 - $25,000'),
        ('25k-50k', '$25,000 - $50,000'),
        ('50k-plus', '$50,000+'),
        ('discuss', "Let's discuss"),
    ]
    
    budget = forms.ChoiceField(
        choices=BUDGET_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white',
        })
    )
    
    TIMELINE_CHOICES = [
        ('', 'When do you need this completed?'),
        ('asap', 'ASAP'),
        ('1-month', 'Within 1 month'),
        ('2-3-months', '2-3 months'),
        ('3-6-months', '3-6 months'),
        ('6-months-plus', '6+ months'),
        ('flexible', 'Timeline is flexible'),
    ]
    
    timeline = forms.ChoiceField(
        choices=TIMELINE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white',
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400',
            'placeholder': 'Please describe your project requirements, goals, and any specific features you have in mind...',
            'rows': 6,
            'required': True,
        }),
        error_messages={
            'required': 'Please provide details about your project.',
        }
    )
    
    # Honeypot field for spam protection
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'style': 'position: absolute; left: -5000px;',
            'aria-hidden': 'true',
            'tabindex': '-1',
            'autocomplete': 'off',
        })
    )
    
    def clean_first_name(self):
        """Validate first name."""
        first_name = self.cleaned_data.get('first_name', '').strip()
        
        if not first_name:
            raise ValidationError('First name is required.')
        
        # Check for minimum length
        if len(first_name) < 2:
            raise ValidationError('First name must be at least 2 characters long.')
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-']+$", first_name):
            raise ValidationError('First name can only contain letters, spaces, hyphens, and apostrophes.')
        
        return first_name.title()
    
    def clean_last_name(self):
        """Validate last name."""
        last_name = self.cleaned_data.get('last_name', '').strip()
        
        if not last_name:
            raise ValidationError('Last name is required.')
        
        # Check for minimum length
        if len(last_name) < 2:
            raise ValidationError('Last name must be at least 2 characters long.')
        
        # Check for valid characters
        if not re.match(r"^[a-zA-Z\s\-']+$", last_name):
            raise ValidationError('Last name can only contain letters, spaces, hyphens, and apostrophes.')
        
        return last_name.title()
    
    def clean_email(self):
        """Validate email address."""
        email = self.cleaned_data.get('email', '').strip().lower()
        
        if not email:
            raise ValidationError('Email address is required.')
        
        # Additional email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError('Please enter a valid email address.')
        
        # Check for common disposable email domains
        disposable_domains = [
            '10minutemail.com', 'guerrillamail.com', 'mailinator.com',
            'tempmail.org', 'throwaway.email'
        ]
        domain = email.split('@')[1]
        if domain in disposable_domains:
            raise ValidationError('Please use a permanent email address.')
        
        return email
    
    def clean_company(self):
        """Validate company name if provided."""
        company = self.cleaned_data.get('company', '').strip()
        
        if company and len(company) > 100:
            raise ValidationError('Company name must be less than 100 characters.')
        
        return company.title() if company else ''
    
    def clean_message(self):
        """Validate message content."""
        message = self.cleaned_data.get('message', '').strip()
        
        if not message:
            raise ValidationError('Please provide details about your project.')
        
        # Check minimum length
        if len(message) < 10:
            raise ValidationError('Message must be at least 10 characters long.')
        
        # Check maximum length
        if len(message) > 2000:
            raise ValidationError('Message must be less than 2000 characters.')
        
        # Basic spam detection
        spam_keywords = ['click here', 'buy now', 'limited time', 'guaranteed', 'free money']
        message_lower = message.lower()
        for keyword in spam_keywords:
            if keyword in message_lower:
                raise ValidationError('Your message appears to contain promotional content.')
        
        return message
    
    def clean(self):
        """Perform form-wide validation."""
        cleaned_data = super().clean()
        
        # Check honeypot field
        website = cleaned_data.get('website')
        if website:
            raise ValidationError('Spam detected. Please try again.')
        
        return cleaned_data
