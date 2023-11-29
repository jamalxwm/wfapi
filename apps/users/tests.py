import pytest
from uuid import UUID
from django.db import IntegrityError
from .models import User as UserModel
from apps.referrals.models import Referral

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

    def test_set_referral_success(self, user):
        code = 'unique code'
        with pytest.raises(ValueError) as e:
            user.set_referral_code(code)

        assert str(e.value) == 'Referral codes can only contain letters, numbers, underscores, and dashes.'

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

@pytest.mark.django_db
class TestCreateUserWithReferral: 
    def test_create_user_with_referral_error(self):
        with pytest.raises(ValueError) as e:
            UserModel.objects.create_user_with_referral(
                email='test@test.com',
                first_name='Test',
                last_name='User',
                password='testpassword123',
                username='test@test.com',
                referral_code='nonexistent'
            )
        assert str(e.value) == 'No user found with referral code nonexistent'

    def test_create_user_with_referral_success(self, user):
        code = 'referred'
        referring_user = user
        referring_user.set_referral_code(code)

        referred_user = UserModel.objects.create_user_with_referral(
                email='test@test.com',
                first_name='Test',
                last_name='User',
                password='testpassword123',
                username='test@test.com',
                referral_code=code
            )
        referring_user.refresh_from_db()
        
        assert referred_user.email == 'test@test.com'
        assert referring_user.referral_count == 1

        referral = Referral.objects.get(referring_user=referring_user, referred_user=referred_user)
        assert referral is not None