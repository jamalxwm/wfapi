import pytest
from faker import Faker
from django_redis import get_redis_connection
from apps.leaderboard.models import Leaderboard, User

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
     
    def test_add_user(self, redis, users, leaderboard):
        # Add users to the leaderboard sorted set
        for index, name in enumerate(users):
            user = User(name)
            user_id = user.user_id
            leaderboard.add_user(user_id, index)

        assert redis.zcard('leaderboard') == self.NUM_USERS
    
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
        assert leaderboard.length == self.NUM_USERS

    def test_get_score_at_rank(self, leaderboard):
        RANK = 5
        EXPECTED_SCORE = 4
        score = leaderboard.get_score_at_rank(RANK)
        
        assert score == EXPECTED_SCORE

    def test_delete_user(self, leaderboard):
        leaderboard.delete_user(self.STATIC_USER)
        assert leaderboard.length == self.NUM_USERS
        assert leaderboard.get_user_rank(self.STATIC_USER) is None


class TestUserCase:

    @pytest.fixture(scope='class', autouse=True)
    def user(self):
        return User("John Doe")

    def test_create_new_user(self, user):
        assert user.user_id == "John Doe"
        assert user.score == 0.0
        assert user.rank == 0
        assert user.team_id == None
        assert user.teammate_id == None

    def test_update_score(self, user):
        user.score = 50.0
        assert user.score == 50.0

    def test_update_rank(self, user):
        user.rank = 23
        assert user.rank == 23

    def test_user_rank_does_not_surpass_zero(self, user):
        user.rank = -100
        assert user.rank == 0
    def test_cannot_leave_team_when_not_on_one(self, user):
        with pytest.raises(Exception):
            user.leave_team()

    def test_join_team(self, user):
        user.join_team('team1', 'Jane Doe')
        assert user.team_id == 'team1'
        assert user.teammate_id == 'Jane Doe'

    def test_cannot_join_team_when_on_one(self, user):
        with pytest.raises(Exception):
            user.join_team('team2', 'Joe Bloggs')

    def test_leave_team(self, user):
        user.leave_team()

        assert user.team_id == None
        assert user.teammate_id == None

    def test_join_team_unknown_error(self, user):
        user._team_id = 'team3'

        with pytest.raises(Exception):
            user.join_team('team1', 'Jane Doe')
       
    def test_join_team_unknown_error(self, user):
        user._team_id = 'team3'

        with pytest.raises(Exception):
            user.leave_team()


@pytest.mark.skip(reason="subject to deletion")
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