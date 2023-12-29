from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.tasks.models import Tasks, UserTasks

User = get_user_model()


class TaskTestCase(TestCase):
    def setUp(self):
        # Create some tasks
        self.task1 = Tasks.objects.create(
            title="Task 1", display_order=1, max_repetitions=1
        )
        self.task2 = Tasks.objects.create(
            title="Task 2", prerequisite=self.task1, display_order=2, max_repetitions=5
        )
        self.task3 = Tasks.objects.create(
            title="Task 3",
            display_order=3,
            is_hidden=True,
            target_demographic="EXPAT",
            max_repetitions=1,
        )
        self.user = User.objects.create_user(
            email="testuser@test.com",
            password="testpass123",
            first_name="test",
            last_name="user",
        )

    def test_user_task_creation(self):
        # Check that UserTask instances have been created
        user_tasks = UserTasks.objects.filter(user=self.user).order_by(
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

    def test_target_demo_user_sees_hidden_task(self):
        # Create a new expat user
        expat_user = User.objects.create_user(
            email="expatuser@test.com",
            password="expatpass123",
            first_name="expat",
            last_name="user",
        )
        # Update the user_profile for the expat_user to set is_expat to True
        expat_user_profile = expat_user.profile
        expat_user_profile.is_expat = True
        expat_user_profile.save()

        # Check that UserTask instances have been created, including the hidden task
        user_tasks = UserTasks.objects.filter(user=expat_user).order_by(
            "task__display_order"
        )
        total_tasks_count = Tasks.objects.count()

        self.assertEqual(user_tasks.count(), total_tasks_count)
        self.assertEqual(user_tasks[2].task.title, "Task 3")
        self.assertEqual(user_tasks[2].state, "AVAILABLE")
        
    def test_single_repitition_task_completes(self):
        user_task = UserTasks.objects.create(user=self.user, task=self.task1)
        user_task.complete()

        self.assertEqual(user_task.state, "COMPLETED")

    def test_multi_repetition_task_stays_available(self):
        user_task = UserTasks.objects.create(
            user=self.user, task=self.task2, state="AVAILABLE"
        )
        user_task.complete()  # First repetition
        user_task.complete()  # Second repetition

        self.assertEqual(user_task.state, "AVAILABLE")
        self.assertEqual(user_task.repetitions, 2)

    def test_dependent_tasks_unlock(self):
        prerequisite_user_task, _ = UserTasks.objects.get_or_create(
            user=self.user, task=self.task1, defaults={"state": "AVAILABLE"}
        )
        dependent_user_task, _ = UserTasks.objects.get_or_create(
            user=self.user, task=self.task2, defaults={"state": "LOCKED"}
        )

        prerequisite_user_task.complete()
        dependent_user_task.refresh_from_db()

        self.assertEqual(dependent_user_task.state, "AVAILABLE")

    def test_repetitions_does_not_surpass_max(self):
        MAX_REPITITIONS = 1
        user_task = UserTasks.objects.create(user=self.user, task=self.task1)
        user_task.complete()
        user_task.complete()
        user_task.complete()

        self.assertEqual(user_task.repetitions, MAX_REPITITIONS)

    def test_completed_task_does_not_complete_again(self):
        user_task = UserTasks.objects.create(
            user=self.user, task=self.task1, state="COMPLETED"
        )
        initial_task_state = user_task.state
        user_task.complete()

        self.assertEqual(user_task.state, initial_task_state)


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

class TaskModelDisplayOrder(TestCase):
    def setUp(self):
        # Create initial tasks with distinct display_orders
        Tasks.objects.create(title='Task 1', display_order=1)
        Tasks.objects.create(title='Task 2', display_order=2)

    def test_unique_display_order(self):
        # Test that a new task with a unique display order doesn't affect others
        task = Tasks(title='Unique Order Task', display_order=3)
        task.save()
        self.assertEqual(Tasks.objects.get(title='Task 1').display_order, 1)
        self.assertEqual(Tasks.objects.get(title='Task 2').display_order, 2)
        self.assertEqual(Tasks.objects.get(title='Unique Order Task').display_order, 3)
    
    def test_duplicate_display_order(self):
        # Test that a new task with a duplicate display order increments others
        task = Tasks(title='Duplicate Order Task', display_order=2)
        task.save()

        # Refresh the objects from the database
        task1 = Tasks.objects.get(title='Task 1')
        task2 = Tasks.objects.get(title='Task 2')
        new_task = Tasks.objects.get(title='Duplicate Order Task')

        # Check the display orders to ensure they have been incremented properly
        self.assertEqual(task1.display_order, 1)  # Should remain unchanged
        self.assertEqual(task2.display_order, 3)  # Should be incremented
        self.assertEqual(new_task.display_order, 2)  # Should take the place of task 2