from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.badges.models import Badge, UserBadge

User = get_user_model()

class Command(BaseCommand):
    help = 'Award badges to users based on certain conditions'

    def handle(self, *args, **options):
            self.award_badges('OG', self.get_og_eligible_users())
            # self.award_badges('Investor', self.get_investor_eligible_users())
            # self.award_badges('Flamingo', self.get_flamingo_eligible_users())
            self.award_badges('Referral King', self.get_referral_eligible_users())

    def get_og_eligible_users(self):
        cutoff_date = timezone.make_aware(timezone.datetime(year=2022, month=1, day=1), timezone.get_default_timezone())
        return User.objects.filter(date_joined__lt=cutoff_date)

    def get_investor_eligible_users(self):
        # User.objects.filter(profile__has_invested=True)
        return User.objects.none()

    def get_flamingo_eligible_users(self):
        # User.objects.filter(profile__is_employee=True)
        return User.objects.none()
    
    def get_referral_eligible_users(self):
        return User.objects.filter(referral_count__gte=10)
    
    def award_badges(self, badge_name, eligible_users):
        try:
            badge = Badge.objects.get(name=badge_name)
            for user in eligible_users:
                UserBadge.objects.get_or_create(user=user, badge=badge)
                self.stdout.write(f'Awarded {badge.name} badge to {user.username}')
        except Badge.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Badge {badge_name} does not exist: {e}'))

