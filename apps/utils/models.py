from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import pytz

class CompanyOfInterest(models.Model):
    domain = models.CharField(max_length=255)

    def __str__(self):
        return self.domain
    
def validate_timezone(value):
    if value not in pytz.all_timezones:
        raise ValidationError(
            _('%(value)s is not a valid timezone'),
            params={'value': value},
        )