from django.db import models

class ChatLead(models.Model):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    page_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_interaction = models.DateTimeField(auto_now=True)
    is_converted = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-last_interaction']
    
    def __str__(self):
        return f"{self.email} - {self.created_at.strftime('%Y-%m-%d')}"

class ChatConversation(models.Model):
    lead = models.ForeignKey(ChatLead, on_delete=models.CASCADE, related_name='conversations')
    messages = models.JSONField(default=list, blank=True, help_text="List of messages in the conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Conversation with {self.lead.email} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"