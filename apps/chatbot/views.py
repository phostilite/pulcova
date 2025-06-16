from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import json
from datetime import datetime
from .models import ChatLead, ChatConversation

@csrf_exempt
def save_chatbot_lead(request):
    """Save chatbot lead information"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create or update lead
            lead, created = ChatLead.objects.update_or_create(
                email=data['email'],
                defaults={
                    'phone': data.get('phone', ''),
                    'page_url': data.get('page_url', ''),
                    'last_interaction': datetime.now()
                }
            )
            
            # Save conversation history
            ChatConversation.objects.create(
                lead=lead,
                messages=data.get('conversation_history', [])
            )
            
            # Send notification email to admin
            send_mail(
                f'New Chat Lead: {data["email"]}',
                f'A new lead has started a conversation:\n\nEmail: {data["email"]}\nPhone: {data.get("phone", "Not provided")}\nPage: {data.get("page_url", "")}\n\nCheck the admin panel for full conversation.',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            
            # Send welcome email to lead
            send_mail(
                'Welcome to Pulcova - We\'ll be in touch!',
                f'Hi there!\n\nThank you for reaching out to Pulcova. We\'ve received your message and someone from our team will get back to you within 24 hours.\n\nIn the meantime, feel free to:\n- Check out our portfolio: https://pulcova.store/portfolio\n- Read our blog: https://pulcova.store/blog\n- Learn about our services: https://pulcova.store/services\n\nBest regards,\nThe Pulcova Team',
                settings.DEFAULT_FROM_EMAIL,
                [data['email']],
                fail_silently=True,
            )
            
            return JsonResponse({'status': 'success', 'lead_id': lead.id})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def save_conversation(request):
    """Save ongoing conversation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            lead = ChatLead.objects.get(email=data['email'])
            
            # Update last conversation
            conversation = ChatConversation.objects.filter(lead=lead).last()
            if conversation:
                conversation.messages = data['messages']
                conversation.save()
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)