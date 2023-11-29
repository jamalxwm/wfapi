from django.db import models
from django.conf import settings


class Referral(models.Model):
    referring_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    referred_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)