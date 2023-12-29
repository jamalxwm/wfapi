To meet the requirements you've described, you'll need to perform several steps, including modifying your models, creating signals to handle user and task creation logic, and writing tests to ensure your implementation works as expected.

### Step 1: Model Adjustments

You might want to adjust the `Tasks` model to ensure that `display_order` is unique, which is important for maintaining a consistent task order:

```python
class Tasks(models.Model):
    # ...
    display_order = models.PositiveIntegerField(unique=True)
    # ...
```

### Step 2: Signals for Automatic UserTask Creation

To populate the `UserTask` table automatically for each new user, you can use Django signals. Specifically, you'll want to use the `post_save` signal for the `User` model to create `UserTask` instances.

Additionally, to handle the creation of new `Tasks` instances and auto-populate `UserTask` for all users, you can use the `post_save` signal for the `Tasks` model.

Here is an example of how you might implement these signals:

```python
# in apps/tasks/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Tasks, UserTask

@receiver(post_save, sender=User)
def create_user_tasks(sender, instance, created, **kwargs):
    if created:
        tasks = Tasks.objects.all().order_by('display_order')
        for task in tasks:
            UserTask.objects.create(user=instance, task=task, state='AVAILABLE' if task.prerequisite is None else 'LOCKED')

@receiver(post_save, sender=Tasks)
def create_tasks_for_all_users(sender, instance, created, **kwargs):
    if created:
        users = User.objects.all()
        for user in users:
            state = 'AVAILABLE' if instance.prerequisite is None else 'LOCKED'
            UserTask.objects.create(user=user, task=instance, state=state)

# Don't forget to connect your signals in the apps.py
```

### Step 3: Overriding `save` Method for `UserTask`

To handle changes in state based on completions and prerequisites, you can override the `save` method of the `UserTask` model:

```python
class UserTask(models.Model):
    # ...

    def save(self, *args, **kwargs):
        if self.completions >= self.task.number_of_completions and self.state != 'COMPLETED':
            self.state = 'COMPLETED'
        super(UserTask, self).save(*args, **kwargs)
        
        # Update dependent tasks
        if self.state == 'COMPLETED':
            for dependent in self.task.dependent_tasks.all():
                user_task, created = UserTask.objects.get_or_create(user=self.user, task=dependent)
                if created or user_task.state != 'COMPLETED':
                    user_task.state = 'AVAILABLE'
                    user_task.save()

    # ...
```

### Step 4: Testing

To test this setup, you'll want to write tests that verify the following:

- When a new user is created, they have the correct `UserTask` instances.
- When a user completes a task, the state of the user's task changes as expected.
- When a new task is added, it appears for all users in the correct state.
- Tasks always present in the same order.

Here's an example of how you might start writing a test for the first case:

```python
# in apps/tasks/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.tasks.models import Tasks, UserTask

User = get_user_model()

class TaskTestCase(TestCase):
    def setUp(self):
        # Create some tasks
        Tasks.objects.create(title='Task 1', display_order=1)
        Tasks.objects.create(title='Task 2', prerequisite=Tasks.objects.get(title='Task 1'), display_order=2)
        # ... more tasks as needed

    def test_user_task_creation(self):
        # Create a new user
        new_user = User.objects.create_user(username='testuser', password='testpass')
        
        # Check that UserTask instances have been created
        user_tasks = UserTask.objects.filter(user=new_user).order_by('task__display_order')
        self.assertEqual(user_tasks.count(), Tasks.objects.count())
        self.assertEqual(user_tasks[0].state, 'AVAILABLE')
        self.assertEqual(user_tasks[1].state, 'LOCKED')

        # ... more assertions as needed
```

### Step 5: Handling Display Order Updates

To handle inserting tasks at specific positions, you have to update the `display_order` of other tasks accordingly. This can be done by overriding the `save` method of the `Tasks` model or by creating a custom method to reorder tasks. This logic would check if there is an existing task with the same `display_order` and increment the `display_order` of all tasks that come after it.

### Step 6: Register### Step 6: Register Signals

To ensure that the signals you've created are connected, you need to import them into your app configuration. In your `apps.py` within the tasks app, you should have something like this:

```python
# in apps/tasks/apps.py
from django.apps import AppConfig

class TasksConfig(AppConfig):
    name = 'apps.tasks'

    def ready(self):
        import apps.tasks.signals  # noqa
```

Make sure to update the `__init__.py` of your tasks app to set the default app configuration:

```python
# in apps/tasks/__init__.py
default_app_config = 'apps.tasks.apps.TasksConfig'
```

### Step 7: Running Tests

You can run your tests using the `manage.py` command:

```sh
python manage.py test apps.tasks
```

This will execute the tests you've defined in the `apps/tasks/tests.py` file.

### Step 8: Admin Interface

For allowing admins to add new entries to tasks later which should populate into the `user_tasks` tables, you should ensure that the admin interface for `Tasks` is set up correctly. You can customize the Django admin to handle the creation of tasks and automatically create `UserTask` instances for all users when a new task is created.

Here's a simple example of how you might set up the admin for the `Tasks` model:

```python
# in apps/tasks/admin.py
from django.contrib import admin
from .models import Tasks, UserTask

@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_order', 'number_of_completions')
    ordering = ('display_order',)

# You can also register UserTask if you want it to be editable in the admin
@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'state', 'completions')
    list_filter = ('state', 'task')
```

### Step 9: Handling `display_order` Updates

For handling updates to `display_order`, you can override the `save` method of the `Tasks` model or use a custom save method in the admin form. Here's a simple approach to update `display_order`:

```python
class Tasks(models.Model):
    # ...

    def save(self, *args, **kwargs):
        if self._state.adding or Tasks.objects.filter(display_order=self.display_order).exists():
            subsequent_tasks = Tasks.objects.filter(display_order__gte=self.display_order).exclude(pk=self.pk)
            for task in subsequent_tasks:
                task.display_order += 1
                task.save(update_fields=['display_order'])
        super(Tasks, self).save(*args, **kwargs)
```

This code will shift the `display_order` of subsequent tasks when a new task is inserted or when the `display_order` of an existing task is updated to a lower number.

Remember that these are starting points. As you work with these systems, you may need to refine and optimize them. For example, bulk updating `display_order` fields or using transactions to ensure data integrity in case of errors during saving could be considered for production systems.