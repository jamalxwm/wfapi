from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.apps import apps
from django.contrib.auth import get_user_model
from .models import UserProfile
from apps.utils.models import CompanyOfInterest
from apps.tasks.utils import assign_hidden_tasks  # Import the utility function

User = get_user_model()

COMPANIES_OF_INTEREST = ['company1.com', 'company2.com']
ACADEMIC_DOMAINS = ['.edu', '.ac.uk']

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

    email_domain = instance.email.split('@')[-1]

    if email_domain in COMPANIES_OF_INTEREST:
        instance.profile.is_company_of_interest = True
        
    if any(email_domain.endswith(academic_domain) for academic_domain in ACADEMIC_DOMAINS):
        instance.profile.is_student = True

    assign_hidden_tasks(instance.profile)

    instance.profile.save()
#     if CompanyOfInterest.objects.filter(domain=email_domain).exists():
#         instance.profile.is_company_of_interest = True

#     # if StudentDomain.objects.filter(domain='.' + email_domain.split('.')[-1]).exists():
#     #     instance.profile.is_student = True
#     # Save the profile if there were any changes
#     instance.profile.save()


