from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import uuid

class User(AbstractUser):
    
    email = models.EmailField(_('email address'), unique=True)
    referral_code = models.CharField(max_length=30, unique=True, null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    # active_tier = models.IntegerField(choices=[(i,i) for i in range(1,5)], default=1)
    # floater = models.ForeignKey('floaters.Floater', on_delete=models.SET_DEFAULT, default=1)

    # def save(self, *args, **kwargs):
#     # Check if floater's tier <= user's active_tier
#     if self.floater.tier_level > self.active_tier:
#         raise ValidationError("A user can only change their floater if the floater is in a tier less than or equal to the tier they're in.")
#     super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.first_name:
            raise ValueError('The First name field must not be empty')
        if not self.last_name:
            raise ValueError('The Last name field must not be empty')
        super().save(*args, **kwargs)

    def set_referral_code(self,code):
        if User.objects.filter(referral_code=code).exists():
            raise ValueError('This referral code is already in use.')
        else:
            self.referral_code = code
            self.save()

    @classmethod
    def create_user(cls, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must not be empty')
        if not password:
            raise ValueError('Password field must not be empty')
        # rest of your code