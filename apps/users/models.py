from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class User(AbstractUser):
    active_tier = models.IntegerField(choices=[(i,i) for i in range(1,5)], default=1)
    floater = models.ForeignKey('floaters.Floater', on_delete=models.SET_DEFAULT, default=1)

    def save(self, *args, **kwargs):
        # Check if floater's tier <= user's active_tier
        if self.floater.tier_level > self.active_tier:
            raise ValidationError("A user can only change their floater if the floater is in a tier less than or equal to the tier they're in.")
        super().save(*args, **kwargs)