from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import gettext as _
from django.apps import apps
import re

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, referral_code=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must not be empty')
        if not password:
            raise ValueError('Password field must not be empty')

        user = self.model(email=self.normalize_email(email), first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        if referral_code:
            self.process_referral(user, referral_code)

        return user

    def process_referral(self, referred_user, referral_code):
        try:
            referring_user = self.model.objects.get(referral_code=referral_code)
        except ObjectDoesNotExist:
            raise ValueError(f'No user found with referral code {referral_code}')
        
        #Create a referral entry
        ReferralModel = apps.get_model('referrals', 'Referral')
        ReferralModel.objects.create(referring_user=referring_user, referred_user=referred_user)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        first_name = extra_fields.pop('first_name', None)
        last_name = extra_fields.pop('last_name', None)
        return self.create_user(email, first_name, last_name, password, **extra_fields)
    
class User(AbstractUser):

    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), max_length=150, unique=False, blank=True, null=True)
    referral_code = models.CharField(max_length=30, unique=True, null=True, blank=True)
    referral_count = models.IntegerField(default=0)
    tier_access = models.IntegerField(default=1, verbose_name=_("Tier access"))
    created_at = models.DateTimeField(auto_now_add=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.first_name:
            raise ValueError('The First name must not be empty')
        if not self.last_name:
            raise ValueError('The Last name must not be empty')
        super().save(*args, **kwargs)

    def set_referral_code(self,code):
        if not re.match('^[A-Za-z0-9_-]*$', code):
            raise ValueError('Referral codes can only contain letters, numbers, underscores, and dashes.')
        if User.objects.filter(referral_code=code).exists():
            raise ValueError('This referral code is already in use.')
        else:
            self.referral_code = code
            self.save()

    def increment_referral_count(user):
        user.referral_count += 1
        user.save(update_fields=['referral_count'])

    def update_user_tier_access(user):
        if user.referral_count >= 25:
            user.tier_access = 4
        elif user.referral_count >= 15:
            user.tier_access = 3
        elif user.referral_count >= 5:
            user.tier_access = 2
        else:
            user.tier_access = 1
        user.save(update_fields=['tier_access'])
