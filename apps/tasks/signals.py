from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Tasks, UserTasks


@receiver(post_save, sender=User)
def create_user_tasks(sender, instance, created, **kwargs):
    if created:
        visible_tasks = Tasks.objects.filter(is_hidden=False).order_by("display_order")
        for task in visible_tasks:
            UserTasks.objects.create(
                user=instance,
                task=task,
                state="AVAILABLE" if task.prerequisite is None else "LOCKED",
            )
