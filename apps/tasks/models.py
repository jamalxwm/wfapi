from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Tasks(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField(blank=True, null=True)
    prerequisite = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='dependent_tasks')
    number_of_completions = models.PositiveIntegerField(default=1)
    display_order = models.PositiveIntegerField()
    no_user_completions = models.PositiveIntegerField(default=0)
    awaiting_completions = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

class UserTask(models.Model):
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