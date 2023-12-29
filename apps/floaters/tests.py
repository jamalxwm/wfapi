from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Floater, FloaterCollection

User = get_user_model()

class FloaterCollectionModelTests(TestCase):
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email="testuser@test.com",
            password="testpass123",
            first_name="test",
            last_name="user",
            )
        # Create a floater
        self.floater = Floater.objects.create(
            display_name="test floater",
            display_description="Lorem ipsum",
            display_order="1",
        )
        # Create a floater collection
        self.collection = FloaterCollection.objects.create(user=self.user)

    def test_floater_collection_creation(self):
        """Test the creation of a FloaterCollection with a given user."""
        self.assertEqual(self.collection.user, self.user)

    def test_floater_collection_floaters(self):
        """Test adding floaters to a FloaterCollection."""
        self.collection.floaters.add(self.floater)
        self.assertIn(self.floater, self.collection.floaters.all())

    def test_floater_collection_user_relation(self):
        """Test the user relationship of a FloaterCollection."""
        self.assertEqual(self.user.floater_collection.get(id=self.collection.id), self.collection)