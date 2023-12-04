import pytest
from faker import Faker
from django_redis import get_redis_connection
from .views import Leaderboard

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

    def test_add_user(self, redis, users, leaderboard):
        # Add users to the leaderboard sorted set
        for index, name in enumerate(users):
            leaderboard.add_user(name, index)

        assert redis.zcard('main_leaderboard') == self.NUM_USERS

    def test_user_rank(self, leaderboard):
        position = max(0, self.NUM_USERS - self.INSERTION_POINT - 1)
        assert leaderboard.get_user_rank(self.STATIC_USER) == position

    def test_user_score(self, leaderboard):
        score = self.INSERTION_POINT
        assert leaderboard.get_user_score(self.STATIC_USER) == score

    def test_increment_user_score(self, leaderboard):
        increment = 5
        leaderboard.increment_user_score(increment, self.STATIC_USER)
        assert leaderboard.get_user_score(self.STATIC_USER) == self.INSERTION_POINT + increment

    def test_get_leaderboard_length(self, leaderboard):
        assert leaderboard.get_leaderboard_length() == self.NUM_USERS

    def test_delete_user(self, leaderboard):
        leaderboard.delete_user(self.STATIC_USER)
        assert leaderboard.get_leaderboard_length() == self.NUM_USERS - 1
        assert leaderboard.get_user_rank(self.STATIC_USER) is None

@pytest.mark.skip(reason="refactoring the leaderboard class")
class TestRankingManager:
    
    def test_update_user_position(self, redis, leaderboard):
        # Update user score and check if it's updated correctly
        start_position = leaderboard.get_user_rank(self.STATIC_USER)
        spaces_to_move = 5
        leaderboard.update_user_rank_by_spaces(self.STATIC_USER, spaces_to_move)

        assert redis.zrevrank('main_leaderboard', self.STATIC_USER) == start_position - spaces_to_move
    
    def test_update_user_position_if_negative_space_jumps(self, redis, leaderboard):
        # Update user score and check if it's updated correctly
        spaces_to_move = 20
        leaderboard.update_user_rank_by_spaces(self.STATIC_USER, spaces_to_move)

        assert redis.zrevrank('main_leaderboard', self.STATIC_USER) == 0