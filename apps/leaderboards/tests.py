import pytest
from faker import Faker
from django_redis import get_redis_connection
from .views import Leaderboards as LeaderboardViews

class TestLeaderboard:
    @pytest.fixture(scope='class', autouse=True)
    def redis(self):
        conn = get_redis_connection('default')
        yield conn
        conn.flushdb()

    @pytest.fixture
    def users(self):
        fake = Faker()
        users = [fake.name() for _ in range(9)]
        users.insert(1, 'static_user')
        return users

    def test_add_user(self, redis, users):
        # Add users to the leaderboard sorted set
        for index, name in enumerate(users):
            LeaderboardViews.add_user(name, index)

        LeaderboardViews.print_leaderboard()
        assert redis.zcard('leaderboard') == 10

    def test_update_user_position(self, redis, users):
        # Update user score and check if it's updated correctly
        LeaderboardViews.update_user_position('static_user', 5)

        LeaderboardViews.print_leaderboard()
        assert redis.zrevrank('leaderboard', 'static_user') == 6