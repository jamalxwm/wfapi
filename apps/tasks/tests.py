from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.tasks.models import Tasks, UserTasks
from apps.users.models import UserProfile

User = get_user_model()


class TaskTestCase(TestCase):
    def setUp(self):
        # Create some tasks
        self.task1 = Tasks.objects.create(title="Task 1", display_order=1, max_user_completions=1)
        self.task2 = Tasks.objects.create(
            title="Task 2",
            prerequisite=self.task1,
            display_order=2,
            max_user_completions=1
        )
        self.task3 = Tasks.objects.create(
            title="Task 3",
            display_order=3,
            is_hidden=True,
            target_demographic="EXPAT",
            max_user_completions=1
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

        visible_tasks_count = Tasks.objects.filter(is_hidden=False).count()

        self.assertEqual(user_tasks.count(), visible_tasks_count)
        self.assertEqual(user_tasks[0].task.title, "Task 1")
        self.assertEqual(user_tasks[0].state, "AVAILABLE")
        self.assertEqual(user_tasks[1].task.title, "Task 2")
        self.assertEqual(user_tasks[1].state, "LOCKED")

        # Ensure that the hidden task has not created a UserTask instance
        with self.assertRaises(IndexError):
            # This will raise an IndexError if there is no third UserTask, which is expected
            hidden_task_state = user_tasks[2].state

#     def test_target_demo_user_sees_hidden_task(self):
#         # Create a new expat user
#         expat_user = User.objects.create_user(
#             email="expatuser@test.com",
#             password="expatpass123",
#             first_name="expat",
#             last_name="user",
#         )
#         # Update the user_profile for the expat_user to set is_expat to True
#         expat_user_profile = expat_user.profile
#         expat_user_profile.is_expat = True
#         expat_user_profile.save()

#         # Check that UserTask instances have been created, including the hidden task
#         user_tasks = UserTasks.objects.filter(user=expat_user).order_by(
#             "task__display_order"
#         )
#         total_tasks_count = Tasks.objects.count()

#         self.assertEqual(user_tasks.count(), total_tasks_count)
#         self.assertEqual(user_tasks[2].task.title, "Task 3")
#         self.assertEqual(user_tasks[2].state, "AVAILABLE")

#     def test_single_completion_task(self):
#         user = User.objects.create_user(email="single@task.com", password="testpass")
#         single_completion_task = Tasks.objects.create(title="Single Completion Task", display_order=4, max_user_completions=1)

#         user_task = UserTasks.objects.create(user=user, task=single_completion_task, state='AVAILABLE')
#         user_task.save()

#         self.assertEqual(user_task.state, 'COMPLETED')

# class TaskModelTests(TestCase):
#     def test_hidden_task_requires_target_demographic(self):
#         # Create a Task with is_hidden=True but no target_demographic
#         task = Tasks(
#             title="Task 1", display_order=1, is_hidden=True, target_demographic=""
#         )

#         # Expect this to raise a ValidationError
#         with self.assertRaises(ValidationError):
#             task.full_clean()

#     def test_visible_task_cannot_have_target_demographic(self):
#         # Create a Task with is_hidden=False and a target_demographic
#         task = Tasks(title='Task 1', display_order=1, is_hidden=False, target_demographic="EXPAT")

#         # Expect this to raise a ValidationError
#         with self.assertRaises(ValidationError):
#             task.full_clean()

#     def test_hidden_task_with_valid_target_demographic(self):
#         # Create a Task with is_hidden=True and a valid target_demographic
#         task = Tasks(title='Task 1', display_order=1, is_hidden=True, target_demographic="EXPAT")

#         # This should not raise a ValidationError
#         try:
#             task.full_clean()
#         except ValidationError:
#             self.fail("full_clean() raised ValidationError unexpectedly!")

#     def test_visible_task_without_target_demographic(self):
#         # Create a Task with is_hidden=False and no target_demographic
#         task = Tasks(title='Task 1', display_order=1, is_hidden=False, target_demographic="")

#         # This should not raise a ValidationError
#         try:
#             task.full_clean()
#         except ValidationError:
#             self.fail("full_clean() raised ValidationError unexpectedly!")
