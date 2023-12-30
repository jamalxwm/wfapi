from django.test import TestCase, override_settings
from .models import Badge, UserBadge
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.utils import timezone
from io import StringIO
import re

User = get_user_model()


class BadgeTestCase(TestCase):
    def setUp(self):
        # Set up any pre-requisites for the Badge tests
        Badge.objects.create(
            name="Gold Star", description="Awarded for excellence in service."
        )

    def test_badge_creation(self):
        # Badges are correctly identified by their name.
        gold_star = Badge.objects.get(name="Gold Star")
        self.assertEqual(gold_star.description, "Awarded for excellence in service.")


class UserBadgeTestCase(TestCase):
    def setUp(self):
        # Create a user and a badge for testing UserBadge
        self.user = User.objects.create_user(
            email="testuser@test.com",
            username="testuser",
            password="12345",
            first_name="firstname",
            last_name="lastname",
        )
        self.badge = Badge.objects.create(
            name="Gold Star", description="Awarded for excellence."
        )

        UserBadge.objects.create(user=self.user, badge=self.badge)

    def test_user_badge_assignment(self):
        """UserBadge correctly links users and badges."""
        user_badge = UserBadge.objects.get(user=self.user, badge=self.badge)
        self.assertEqual(user_badge.user.username, "testuser")
        self.assertEqual(user_badge.badge.name, "Gold Star")


class AwardBadgesCommandTest(TestCase):
    def setUp(self):
        # Create badges
        self.og_badge = Badge.objects.create(name="OG", description="Original gangster")
        self.referral_king_badge = Badge.objects.create(
            name="Referral King", description="Referral master"
        )

        # Create users
        self.old_user = User.objects.create_user(
            email="olduser@test.com",
            username="old_user",
            password="12345",
            first_name="firstname",
            last_name="lastname",
            date_joined=timezone.now() - timezone.timedelta(days=365 * 2),
        )
        self.referral_user = User.objects.create_user(
            email="refuser@test.com",
            username="referral_user",
            password="12345",
            first_name="firstname",
            last_name="lastname",
            referral_count=10,
        )

    def test_command_awards_badges_correctly(self):
        # Prepare to capture the command output
        out = StringIO()

        # Call the command
        call_command("award_badges", stdout=out)

        # Check if the command output contains expected strings
        self.assertIn("Awarded OG badge to old_user", out.getvalue())
        self.assertIn("Awarded Referral King badge to referral_user", out.getvalue())

        # Check if the badges were actually awarded
        self.assertTrue(
            UserBadge.objects.filter(user=self.old_user, badge=self.og_badge).exists()
        )
        self.assertTrue(
            UserBadge.objects.filter(
                user=self.referral_user, badge=self.referral_king_badge
            ).exists()
        )

    def test_command_handles_nonexistent_badge_gracefully(self):
        # Delete a badge to simulate the error condition
        self.og_badge.delete()

        # Prepare to capture the command output
        out = StringIO()

        # Call the command
        call_command("award_badges", stdout=out)

        # Get the command output and remove the ANSI escape sequences for color coding
        command_output = out.getvalue()
        ansi_escape = re.compile(r'\x1b\[31;1m|\x1b\[0m')
        clean_output = ansi_escape.sub('', command_output)

        # Check if the cleaned command output contains expected error message
        self.assertIn("Badge OG does not exist:", clean_output)
