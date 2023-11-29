import pytest
from uuid import UUID
from django.db import IntegrityError
from .models import User as UserModel

@pytest.fixture
def user():
    return UserModel.objects.create_user(
        email='testuser@test.com',
        first_name='Test',
        last_name='User',
        password='testpassword123',
        username='testuser@test.com'
    )

@pytest.mark.django_db
class TestCreateUser:   
    def test_create_user(self, user):
        assert user.email == 'testuser@test.com'

    def test_create_user_without_email(self):
        with pytest.raises(ValueError):
            user = UserModel.objects.create_user(
                email='',
                first_name='Test',
                last_name='User',
                password='testpassword123',
                username=''
            )
            

    def test_create_user_without_first_name(self):
        with pytest.raises(ValueError):
            UserModel.objects.create_user(
                email='testuser2@test.com',
                first_name='',
                last_name='User',
                password='testpassword123',
                username='testuser2@test.com'
            )

    def test_create_user_with_duplicate_email(self):
        UserModel.objects.create_user(
                email='testuser@test.com',
                first_name='Test',
                last_name='User',
                password='testpassword123',
                username='testuser@test.com',
            )
        with pytest.raises(IntegrityError):
            duplicate_user = UserModel.objects.create_user(
                email='testuser@test.com',
                first_name='Test',
                last_name='User',
                password='testpassword123',
                username='testuser@test.com',
            )

@pytest.mark.django_db
class TestCreateReferralCode:
    def test_set_referral_success(self, user):
        code = 'unique-code'

        user.set_referral_code(code)

        user = UserModel.objects.get(username='testuser@test.com')
        assert user.referral_code == code

    def test_set_duplicate_referral_code(self, user):
        code = 'non-unique-code'
        user.set_referral_code(code)

        user2 = UserModel.objects.create_user(
                email='testuser2@test.com',
                first_name='Test',
                last_name='User',
                password='testpassword123',
                username='testuser2@test.com'
        )
        with pytest.raises(ValueError) as e:
            user2.set_referral_code(code)

        assert str(e.value) == 'This referral code is already in use.'

        user2 = UserModel.objects.get(username='testuser2@test.com')
        assert user2.referral_code is None