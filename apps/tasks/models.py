from django.db import models, transaction
from django.db.models import F
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class Tasks(models.Model):
    TARGET_DEMO_CHOICES = [
        ("EXPAT", "Expat"),
        ("PARENT", "Parent"),
        ("SPORTS", "Sports"),
        ("FESTIVAL", "Festival"),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=255, blank=True)
    uri = models.URLField(blank=True, null=True)
    queue_jumps = models.PositiveBigIntegerField(blank=False, default=10)

    prerequisite = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dependent",
    )
    max_repetitions = models.PositiveIntegerField(
        default=1, help_text="Maximum number of times a user can repeat a task."
    )
    display_order = models.PositiveIntegerField(unique=True)
    total_global_completions = models.PositiveIntegerField(
        default=0, help_text="Total completions by all users."
    )
    pending_global_completions = models.PositiveIntegerField(
        default=0,
        help_text="Number of users who have this task available but have not completed it.",
    )
    is_hidden = models.BooleanField(default=False, null=False)
    target_demographic = models.CharField(
        max_length=25, choices=TARGET_DEMO_CHOICES, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # If the task is hidden, target_demographic must be set
        if self.is_hidden and not self.target_demographic:
            raise ValidationError(
                {
                    "target_demographic": _(
                        "This field must be set when the task is hidden."
                    )
                }
            )

        # If the task is not hidden, target_demographic must be blank
        if not self.is_hidden and self.target_demographic:
            raise ValidationError(
                {
                    "target_demographic": _(
                        "This field must be blank when the task is not hidden."
                    )
                }
            )
            
    def save(self, *args, **kwargs):
        with transaction.atomic():
            # If the task is being added, not updated
            if self._state.adding:
                # If a task with the same display_order exists, increment all subsequent tasks
                if Tasks.objects.filter(display_order=self.display_order).exists():
                    Tasks.objects.filter(display_order__gte=self.display_order)\
                        .order_by('-display_order')\
                        .update(display_order=F('display_order') + 1)
            
            self.full_clean()  # Validate now, after re-ordering logic
            super().save(*args, **kwargs)  # Save the current instance

    def __str__(self):
        return self.title


class UserTasks(models.Model):
    STATE_CHOICES = [
        ("AVAILABLE", "Available"),
        ("LOCKED", "Locked"),
        ("HIDDEN", "Hidden"),
        ("COMPLETED", "Completed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    state = models.CharField(max_length=10, choices=STATE_CHOICES)
    repetitions = models.PositiveIntegerField(default=0)

    def complete(self):
        # Mark the task as completed and handle related logic.
        if self.state != "COMPLETED":
            self.repetitions += 1
            if self.repetitions >= self.task.max_repetitions:
                self.state = "COMPLETED"
            # Unlock dependent tasks
            self._unlock_dependent_tasks()
            self.save()

    def _unlock_dependent_tasks(self):
        # Unlock tasks that are dependent on the completion of this task.
        for dependent in self.task.dependent.all():
            user_task, created = UserTasks.objects.get_or_create(
                user=self.user, task=dependent
            )
            if created or user_task.state != "COMPLETED":
                user_task.state = "AVAILABLE"
                user_task.save()

    def save(self, *args, **kwargs):
        # The save method now only calls the superclass's save method.
        # All business logic is handled in other methods.
        super(UserTasks, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.task.title}"
