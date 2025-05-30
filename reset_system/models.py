from django.db import models
from django.contrib.auth.models import User

class PasswordResetRequest(models.Model):
    SYSTEM_CHOICES = [
        ('windows', 'Windows System'),('efinancials', 'Efinancials')
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('recommended', 'Recommended'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('completed', 'Completed'),
    ]

    requestor = models.ForeignKey(User, on_delete=models.CASCADE)
    system = models.CharField(max_length=50, choices=SYSTEM_CHOICES)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deputy_director_comments = models.TextField(blank=True, null=True)
    cto_comments = models.TextField(blank=True, null=True)
    ict_personnel = models.ForeignKey(User, related_name='ict_actions', on_delete=models.SET_NULL, null=True,
                                      blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.requestor.username} - {self.system} - {self.status}"