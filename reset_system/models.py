from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,  # Only allow blank for deputy directors/CTO
        help_text="Required for regular staff"
    )
    is_deputy_director = models.BooleanField(default=False)
    is_ict_head = models.BooleanField(default=False)
    is_ict_admin = models.BooleanField(default=False)
    is_service_desk = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.department.name if self.department else 'Admin'})"

class PasswordResetRequest(models.Model):
    SYSTEM_CHOICES = [
        ('windows', 'Windows System'),('efinancials', 'Efinancials')
    ]

    RESET_REASONS = [
        ('forgot_password', 'Forgot Password'),
        ('locked_account', 'Locked Account'),
        ('expired_password', 'Expired Password'),
        ('security_issue', 'Security Issue'),
        ('other', 'Other'),
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
    reason = models.CharField(
        max_length=50,
        choices=RESET_REASONS,
        blank=False,  # 👈 required field
        null=False
    )
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approvals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_ict_head = models.BooleanField(default=False)
    deputy_director_comments = models.TextField(blank=True, null=True)
    cto_comments = models.TextField(blank=True, null=True)
    ict_personnel = models.ForeignKey(User, related_name='ict_actions', on_delete=models.SET_NULL, null=True,
                                      blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.requestor.username} - {self.system} - {self.status}"