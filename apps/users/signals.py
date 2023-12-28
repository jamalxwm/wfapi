from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserProfile, User
from apps.utils.models import CompanyOfInterest


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)
#     instance.profile.save()

#     email_domain = instance.email.split('@')[1]

#     if CompanyOfInterest.objects.filter(domain=email_domain).exists():
#         instance.profile.is_company_of_interest = True

#     # if StudentDomain.objects.filter(domain='.' + email_domain.split('.')[-1]).exists():
#     #     instance.profile.is_student = True
#     # Save the profile if there were any changes
#     instance.profile.save()

# @receiver(post_save, sender=User)
# def update_tier(sender, instance, **kwargs):
#     instance.update_user_tier()