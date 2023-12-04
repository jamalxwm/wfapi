import pytest
from faker import Faker
from django_redis import get_redis_connection
from .views import Leaderboard, SoloRanks

class TestMainLeaderboard:
    NUM_USERS = 10
    STATIC_USER = 'static_user'
    INSERTION_POINT = 8

    @pytest.fixture(scope='class', autouse=True)
    def redis(self):
        conn = get_redis_connection('default')
        yield conn
        conn.flushdb()

    @pytest.fixture
    def users(self):
        fake = Faker()
        users = [fake.name() for _ in range(self.NUM_USERS - 1)]
        users.insert(self.INSERTION_POINT, self.STATIC_USER)
        return users

    @pytest.fixture
    def leaderboard(request):
        leaderboard = Leaderboard('main_leaderboard')
        yield leaderboard
        # After the test, reset the singleton instance to None
        type(leaderboard)._instance = None
