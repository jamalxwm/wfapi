from django.db import models
from django.conf import settings

class Floater(models.Model):
    STARTER_PACK = 'ST'
    TRIED_TRUE = 'TT'
    BADDIES = 'BD'
    GOD = 'GD'
    
    TIER_CHOICES = [
        (STARTER_PACK, 'Starter Pack'),
        (TRIED_TRUE, 'Tried & True'),
        (BADDIES, 'Baddies'),
        (GOD, 'God Tier'),
    ]
    TIER_LEVELS = {
        STARTER_PACK: 1,
        TRIED_TRUE: 2,
        BADDIES: 3,
        GOD: 4,
    }

    TIER_JUMPS = {
        STARTER_PACK: 10,
        TRIED_TRUE: 20,
        BADDIES: 50,
        GOD: 75,
    }

    display_name = models.CharField(max_length=25)
    display_description = models.TextField(default='enter some text')
    display_order = models.IntegerField(unique=True, null=False)
    short_description = models.CharField(default='short')
    tier = models.CharField(max_length=2, choices=TIER_CHOICES, default=STARTER_PACK)
    avatar_icon_1x = models.ImageField(upload_to='floaters/icons', blank=True, null=True)
    avatar_icon_2x = models.ImageField(upload_to='floaters/icons', blank=True, null=True)
    avatar_hero_1x = models.ImageField(upload_to='floaters/heroes', blank=True, null=True)
    avatar_hero_2x = models.ImageField(upload_to='floaters/heroes', blank=True, null=True)
    avatar_badge_1x = models.ImageField(upload_to='floaters/badges', blank=True, null=True)
    avatar_badge_2x = models.ImageField(upload_to='floaters/badges', blank=True, null=True)

    @property
    def tier_level(self):
        return self.TIER_LEVELS[self.tier]
    
    @property
    def tier_jumps(self):
        return self.TIER_JUMPS[self.tier]
    
    def __str__(self):
        return self.display_name

class FloaterCollection(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='floater_collection')
    floaters = models.ManyToManyField(Floater, related_name='collections', blank=True)

    def add_floater(self, floater):
        # Add a floater to the collection
        if not self.floaters.filter(id=floater.id).exists():
            self.floaters.add(floater)

    def remove_floater(self, floater):
        # Remove a floater from the collection
        self.floaters.remove(floater)