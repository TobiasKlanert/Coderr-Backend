from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    file = models.FileField(upload_to='profile_pictures/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, default='')
    tel = models.CharField(max_length=32, blank=True, default='')
    description = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=64, blank=True, default='')
    type = models.CharField(max_length=32, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    created_at = models.DateTimeField(blank=True, default='')#auto_now_add=True)

    def __str__(self) -> str:
        return f"UserProfile(user_id={self.user_id})"
