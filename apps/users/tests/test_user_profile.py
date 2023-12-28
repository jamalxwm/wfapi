from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.users.models import UserProfile

User = get_user_model()

class UserProfileSignalTest(TestCase):
    def test_user_profile_creation_for_company_of_interest(self):
        # Email domain that matches one of the companies of interest
        email = 'newuser@company1.com'
        user = User.objects.create_user(username=email, email=email, password='testpass123', first_name='test', last_name='user')

        # Fetch the created user profile
        user_profile = UserProfile.objects.get(user=user)

        # Assertions to ensure the user profile is created and linked
        self.assertIsNotNone(user_profile, "UserProfile should be created.")
        self.assertEqual(user_profile.user, user, "UserProfile should be linked to the correct user.")
        self.assertTrue(user_profile.is_company_of_interest)
       
    def test_user_profile_creation_for_student(self):
        # Email domain that matches an academic domain
        email = 'newuser@university.edu'
        user = User.objects.create_user(username=email, email=email, password='testpass123', first_name='test', last_name='user')

        # Fetch the created user profile
        user_profile = UserProfile.objects.get(user=user)

        # Assertions to ensure the user profile is created and linked
        self.assertIsNotNone(user_profile, "UserProfile should be created.")
        self.assertEqual(user_profile.user, user, "UserProfile should be linked to the correct user.")
        self.assertTrue(user_profile.is_student)

    def test_user_profile_creation_for_non_interest_company(self):
        # Email domain that does not match the companies of interest
        email = 'newuser@noninterest.com'
        user = User.objects.create_user(username=email, email=email, password='testpass123', first_name='test', last_name='user')

        # Fetch the created user profile
        user_profile = UserProfile.objects.get(user=user)

        # Assertions to ensure the user profile is created and linked
        self.assertIsNotNone(user_profile, "UserProfile should be created.")
        self.assertEqual(user_profile.user, user, "UserProfile should be linked to the correct user.")
        self.assertFalse(user_profile.is_company_of_interest)
        self.assertFalse(user_profile.is_student)
        