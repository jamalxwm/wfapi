from celery import shared_task
from .models import UserProfile
from apps.tasks.models import UserTasks
from django.contrib.auth.models import User

@shared_task
def create_user_profile(user_id):
    user = User.objects.get(pk=user_id)
    UserTasks.objects.get_or_create(user=user)
    UserProfile.objects.get_or_create(user=user)

