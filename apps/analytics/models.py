from django.db import models


class PageView(models.Model):
    path = models.CharField(max_length=500)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    referrer = models.URLField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.path} - {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']
