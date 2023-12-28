from django.contrib.auth import get_user_model
from apps.referrals.models import Referral

class UserReferralsService:
    @staticmethod
    def get_referred_users(user):
        referred_users_ids = Referral.objects.get_referred_users(user)
        User = get_user_model()
        referred_users = User.objects.filter(id__in=referred_users_ids)
        return referred_users
