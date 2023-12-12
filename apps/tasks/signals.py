from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserTask

@receiver(post_save, sender=UserTask)
def unlock_dependent_tasks(sender, instance, **kwargs):
    if instance.state == 'COMPLETED':
        UserTask.objects.filter(
            user=instance.user,
            task__prerequisite=instance.task,
            state='LOCKED'
        ).update(state='AVAILABLE')