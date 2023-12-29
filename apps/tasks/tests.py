from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.tasks.models import Tasks, UserTasks

User = get_user_model()


class TaskTestCase(TestCase):
    def setUp(self):
        # Create some tasks
        Tasks.objects.create(title="Task 1", display_order=1)
        Tasks.objects.create(
            title="Task 2",
            prerequisite=Tasks.objects.get(title="Task 1"),
            display_order=2,
        )

    def test_user_task_creation(self):
        # Create a new user
        new_user = User.objects.create_user(
            email="testuser@test.com",
            password="testpass123",
            first_name="test",
            last_name="user",
        )

        # Check that UserTask instances have been created
        user_tasks = UserTasks.objects.filter(user=new_user).order_by(
            "task__display_order"
        )
        self.assertEqual(user_tasks.count(), Tasks.objects.count())
        self.assertEqual(user_tasks[0].state, "AVAILABLE")
        self.assertEqual(user_tasks[1].state, "LOCKED")


class TaskModelTests(TestCase):
    def test_hidden_task_requires_target_demographic(self):
        # Create a Task with is_hidden=True but no target_demographic
        task = Tasks(
            title="Task 1", display_order=1, is_hidden=True, target_demographic=""
        )

        # Expect this to raise a ValidationError
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_visible_task_cannot_have_target_demographic(self):
        # Create a Task with is_hidden=False and a target_demographic
        task = Tasks(title='Task 1', display_order=1, is_hidden=False, target_demographic="EXPAT")

        # Expect this to raise a ValidationError
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_hidden_task_with_valid_target_demographic(self):
        # Create a Task with is_hidden=True and a valid target_demographic
        task = Tasks(title='Task 1', display_order=1, is_hidden=True, target_demographic="EXPAT")

        # This should not raise a ValidationError
        try:
            task.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexpectedly!")

    def test_visible_task_without_target_demographic(self):
        # Create a Task with is_hidden=False and no target_demographic
        task = Tasks(title='Task 1', display_order=1, is_hidden=False, target_demographic="")

        # This should not raise a ValidationError
        try:
            task.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexpectedly!")
