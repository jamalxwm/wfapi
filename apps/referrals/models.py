from django.db import models
from django.conf import settings

class ReferralManager(models.Manager):
    def get_referred_users(self, user):
        return self.get_queryset().filter(referring_user=user).values_list('referred_user', flat=True)
    
class Referral(models.Model):
    referring_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ReferralManager()

    def __str__(self):
        return f"{self.referring_user} referred {self.referred_user}"