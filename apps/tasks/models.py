from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Tasks(models.Model):
    TARGET_DEMO_CHOICES = [
        ('EXPAT', 'Expat'),
        ('PARENT', 'Parent'),
        ('SPORTS', 'Sports'),
        ('FESTIVAL', 'Festival'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=255, blank=True)
    uri = models.URLField(blank=True, null=True)
    queue_jumps = models.PositiveBigIntegerField(blank=False, default=10)
    
    prerequisite = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='dependent_tasks')
    max_user_completions = models.PositiveIntegerField(default=1, help_text="Maximum completions allowed per user.")
    display_order = models.PositiveIntegerField(unique=True)
    total_global_completions = models.PositiveIntegerField(default=0, help_text="Total completions by all users.")
    pending_global_completions = models.PositiveIntegerField(default=0, help_text="Number of users who have this task available but have not completed it.")
    is_hidden = models.BooleanField(default=False, null=False)
    target_demographic = models.CharField(max_length=25, choices=TARGET_DEMO_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # If the task is hidden, target_demographic must be set
        if self.is_hidden and not self.target_demographic:
            raise ValidationError({
                'target_demographic': _("This field must be set when the task is hidden.")
            })

        # If the task is not hidden, target_demographic must be blank
        if not self.is_hidden and self.target_demographic:
            raise ValidationError({
                'target_demographic': _("This field must be blank when the task is not hidden.")
            })

    def save(self, *args, **kwargs):
        self.full_clean()  # Call the full_clean method to run validation
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class UserTasks(models.Model):
    STATE_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('LOCKED', 'Locked'),
        ('HIDDEN', 'Hidden'),
        ('COMPLETED', 'Completed')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    state = models.CharField(max_length=10, choices=STATE_CHOICES)
    completions = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.task.title}"