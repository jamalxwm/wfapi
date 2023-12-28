from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps

@receiver(post_save, sender=apps.get_model('referrals', 'Referral'))
def update_user_referral_status(sender, instance, created, **kwargs):
    if created:
        referring_user = instance.referring_user
        referring_user.increment_referral_count()
        referring_user.update_user_tier_access()