import pytest
from faker import Faker
from django_redis import get_redis_connection
from apps.leaderboard.models import Leaderboard, Player


class TestLeaderboard:
    NUM_USERS = 10
    STATIC_USER = 'static_user'
    INSERTION_POINT = 9

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
        leaderboard = Leaderboard()
        yield leaderboard
        # After the test, reset the singleton instance to None
        type(leaderboard)._instance = None
     
    def test_add_player(self, redis, users, leaderboard):
        # Add users to the leaderboard sorted set
        for index, name in enumerate(users):
            user = Player(name)
            user_id = user.user_id
            leaderboard.add_player(user_id, index)

        assert redis.zcard('leaderboard') == self.NUM_USERS

    def test_get_user_rank(self)
