from django.test import TestCase
from django.utils.timezone import timezone, now
from .models import (
    DeviceSession,
    UserDevice,
)
from django.contrib.auth import get_user_model

User = get_user_model()

class DeviceSessionModelTests(TestCase):
    def setUp(self):
        # Setup a user and user device for testing
        self.user = User.objects.create_user(
            email="testuser@test.com",
            first_name="Test",
            last_name="User",
            password="testpassword123",
            username="testuser@test.com",
        )
        self.user_device = UserDevice.objects.create(
            user=self.user,
            device_fingerprint='unique_fingerprint',
            device_model="Model X",
            device_brand="Brand Y",
            os_name="OS Name",
            os_version="OS Version",
            screen_width=1920,
            screen_height=1080,
            locales=["en-US"],
            currencies=["USD"],
            font_scale=1.0,
            accesibility_settings={"high_contrast": True},
            created_at=now(),
            updated_at=now()
        )
        self.ip_address = "127.0.0.1"
        self.timezone_str = "UTC"

    def test_start_new_session(self):
        # Test that a new session can be started
        session = DeviceSession.start_session(
            user_device=self.user_device,
            ip=self.ip_address,
            timezone_str=self.timezone_str,
        )
        self.assertIsInstance(session, DeviceSession)
        self.assertTrue(session.is_active())
        self.assertIsNone(session.session_end)
        self.assertIsNotNone(session.session_start)
        self.assertEqual(session.ip, self.ip_address)
        self.assertEqual(session.timezone, self.timezone_str)

    def test_session_is_active(self):
        # Test the is_active method for an ongoing session
        session = DeviceSession.start_session(
            user_device=self.user_device,
            ip=self.ip_address,
            timezone_str=self.timezone_str,
        )
        self.assertTrue(session.is_active())

        # End the session and test is_active again
        session.end_session()
        self.assertFalse(session.is_active())

    def test_session_soft_delete(self):
        # Test the soft delete method
        session = DeviceSession.start_session(
            user_device=self.user_device,
            ip=self.ip_address,
            timezone_str=self.timezone_str,
        )
        self.assertTrue(session.is_active())

        # Soft delete the session and test is_active
        session.soft_delete()
        self.assertFalse(session.is_active())
