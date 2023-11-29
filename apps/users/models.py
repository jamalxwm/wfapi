from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from django.apps import apps
import re

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must not be empty')
        if not password:
            raise ValueError('Password field must not be empty')

        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user_with_referral(self, email, first_name, last_name, referral_code, password=None, **extra_fields):
        # Find the referring user
        try:
            referring_user = self.model.objects.get(referral_code=referral_code)
        except ObjectDoesNotExist:
            raise ValueError(f'No user found with referral code {referral_code}')

        # Create a new user
        new_user = self.create_user(email, first_name, last_name, password)

        #Create a referral entry
        ReferralModel = apps.get_model('referrals', 'Referral')
        ReferralModel.objects.create(referring_user=referring_user, referred_user=new_user)

        # Increase referral count for the referring user
        referring_user.increment_referral_count()

        return new_user

class User(AbstractUser):

    email = models.EmailField(_('email address'), unique=True)
    referral_code = models.CharField(max_length=30, unique=True, null=True, blank=True)
    referral_count = models.IntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.first_name:
            raise ValueError('The First name field must not be empty')
        if not self.last_name:
            raise ValueError('The Last name field must not be empty')
        super().save(*args, **kwargs)

    def set_referral_code(self,code):
        if not re.match('^[A-Za-z0-9_-]*$', code):
            raise ValueError('Referral codes can only contain letters, numbers, underscores, and dashes.')
        if User.objects.filter(referral_code=code).exists():
            raise ValueError('This referral code is already in use.')
        else:
            self.referral_code = code
            self.save()

    def increment_referral_count(self):
        self.referral_count += 1
        self.save()