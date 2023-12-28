from django.db import models
from django.conf import settings
from django_countries.fields import CountryField
from django.utils.translation import gettext as _


class UserProfile(models.Model):
    # Link to the User model
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    
    PRONOUN_CHOICES = (
    ('he', 'He/Him/His'),
    ('she', 'She/Her/Hers'),
    ('they', 'They/Them/Theirs'),
    ('other', 'Other'),
    )

    # Biographical data
    dob = models.DateField(verbose_name=_("Date of Birth"), null=True)
    phyiscal_location = CountryField(verbose_name=_("Country"), blank_label='(Select country)')
    pronouns = models.CharField(max_length=30, verbose_name=_("Pronouns"), choices=PRONOUN_CHOICES)
    
    # Avatar info
    avatar_id = models.ForeignKey('floaters.Floater', on_delete=models.CASCADE, verbose_name=_("Floater ID"), null=True)
    
    # User ravel habits
    is_expat = models.BooleanField(default=False, verbose_name=_("Is Expat"))
    is_parent = models.BooleanField(default=False, verbose_name=_("Is Parent"))
    is_sports_traveler = models.BooleanField(default=False, verbose_name=_("Is Sports Traveler"))
    is_festival_traveler = models.BooleanField(default=False, verbose_name=_("Is Festival Traveler"))
    
    # User associations
    is_student = models.BooleanField(default=False)
    is_vip = models.BooleanField(default=False)
    is_company_of_interest = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


