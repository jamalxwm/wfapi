import pytest
from faker import Faker
from django_redis import get_redis_connection
from apps.leaderboard.models import Leaderboard, Player


class TestLeaderboard:
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
    
    def test_player_rank(self, leaderboard):
        position = max(0, self.NUM_USERS - self.INSERTION_POINT - 1)
        assert leaderboard.get_player_rank(self.STATIC_USER) == position

    def test_player_score(self, leaderboard):
        score = self.INSERTION_POINT
        assert leaderboard.get_player_score(self.STATIC_USER) == score

    def test_increment_player_score(self, leaderboard):
        increment = 5
        leaderboard.increment_player_score(increment, self.STATIC_USER)
        assert leaderboard.get_player_score(self.STATIC_USER) == self.INSERTION_POINT + increment

    def test_update_player_score(self, leaderboard):
        NEW_SCORE = 10.0
        leaderboard.update_player_score(self.STATIC_USER, NEW_SCORE)
   
        assert leaderboard.get_player_score(self.STATIC_USER) == NEW_SCORE

    def test_update_player_score_does_not_add_users(self, leaderboard):
        NEW_SCORE = 10.0
        NEW_USER = 'new_user'
        leaderboard.update_player_score(NEW_USER, NEW_SCORE)

        assert leaderboard.get_player_rank(NEW_USER) == None
   
    def test_get_leaderboard_length(self, leaderboard, redis):
        assert leaderboard.length == self.NUM_USERS

    def test_get_score_at_rank(self, leaderboard):
        RANK = 5
        EXPECTED_SCORE = 4
        score = leaderboard.get_score_at_rank(RANK)
        
        assert score == EXPECTED_SCORE

    def test_delete_player(self, leaderboard):
        leaderboard.delete_player(self.STATIC_USER)
        assert leaderboard.length == self.NUM_USERS
        assert leaderboard.get_player_rank(self.STATIC_USER) is None

