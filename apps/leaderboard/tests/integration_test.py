import pytest
from faker import Faker
from django_redis import get_redis_connection
from apps.leaderboard.models import Leaderboard
from app.leaderboard.manager import RankingManager

class TestLeaderboardRankingManager:
    NUM_USERS = 100
    STATIC_USER = 'static_user'
    INSERTION_POINT = 8

    @pytest.fixture(scope='class', autouse=True)
    def redis(self):
        conn = get_redis_connection('default')
        yield conn
        conn.flushdb()

    @pytest.fixture(scope='class', autouse=True)
    def users(self):
        fake = Faker()
        users = [fake.name() for _ in range(self.NUM_USERS - 1)]
        users.insert(self.INSERTION_POINT, self.STATIC_USER)
        return users

    @pytest.fixture(scope='class', autouse=True)
    def leaderboard(self, users):
        leaderboard = Leaderboard()
        for index, name in enumerate(users):
            self.leaderboard.add_user(index, name)
        yield leaderboard
        # After the test, reset the singleton instance to None
        type(leaderboard)._instance = None

    def test_ranking_mgr_lb_interaction(self, redis):
        score = redis.zscore(self.leaderboard, 'static_user')
        print(f'STATIC USER SCORE is {score}')