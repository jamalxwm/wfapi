from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.users.services import UserReferralsService
from apps.referrals.models import Referral

User = get_user_model()

class ReferralServiceTestCase(TestCase):
    def create_test_user(
        self,
        username,
        password="testpass123",
        email=None,
        first_name="Test",
        last_name="User",
        referral_code=None,
        **extra_fields,
    ):
        # Provide default values for email and names if they aren't specified
        email = email or f"{username}@example.com"

        return User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            referral_code=referral_code,
            **extra_fields,
        )

    def setUp(self):
        # Create a user who will make referrals
        self.referring_user = self.create_test_user("referrer")

        # Create some referred users
        self.referred_user_1 = self.create_test_user("referred1")
        self.referred_user_2 = self.create_test_user("referred2")
        self.referred_user_3 = self.create_test_user("referred3")

        # Create referrals
        Referral.objects.create(
            referring_user=self.referring_user, referred_user=self.referred_user_1
        )
        Referral.objects.create(
            referring_user=self.referring_user, referred_user=self.referred_user_2
        )
        Referral.objects.create(
            referring_user=self.referring_user, referred_user=self.referred_user_3
        )

    def test_get_referred_users(self):
        # Use the service to get referred users
        referred_users = UserReferralsService.get_referred_users(self.referring_user)

        # Check that we got the right users back
        self.assertIn(self.referred_user_1, referred_users)
        self.assertIn(self.referred_user_2, referred_users)
        self.assertEqual(referred_users.count(), 3)

