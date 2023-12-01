import pytest
from faker import Faker
from django_redis import get_redis_connection
from .views import Leaderboards as LeaderboardViews

class TestMainLeaderboard:
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

    @pytest.fixture
    def leaderboard(self):
        return LeaderboardViews('main_leaderboard')

    def test_add_user(self, redis, users, leaderboard):
        # Add users to the leaderboard sorted set
        for index, name in enumerate(users):
            leaderboard.add_user(name, index)

        assert redis.zcard('main_leaderboard') == 10

    def test_user_position(self, redis, leaderboard):
        position = leaderboard.get_user_rank('static_user')

        assert position - 1 == redis.zrevrank('main_leaderboard', 'static_user')

    def test_update_user_position(self, redis, leaderboard):
        # Update user score and check if it's updated correctly
        start_position = leaderboard.get_user_rank('static_user') - 1
        spaces_to_move = 5
        leaderboard.update_user_rank_by_spaces('static_user', spaces_to_move)

        assert redis.zrevrank('main_leaderboard', 'static_user') == start_position - spaces_to_move

    def test_update_user_position_if_negative_space_jumps(self, redis, leaderboard):
        # Update user score and check if it's updated correctly
        spaces_to_move = 20
        leaderboard.update_user_rank_by_spaces('static_user', spaces_to_move)

        assert redis.zrevrank('main_leaderboard', 'static_user') == 0

    def test_get_leaderboard_length(self, leaderboard):
        assert leaderboard.get_leaderboard_length() == 10

    def test_delete_user(self, redis, leaderboard):
        leaderboard.delete_user('static_user')
        assert redis.zcard('main_leaderboard') == 9


class TestIndividualLeaderboard:
    @pytest.fixture(scope='class', autouse=True)
    def redis(self):
        conn = get_redis_connection('default')
        yield conn
        conn.flushall()

    @pytest.fixture
    def users(self):
        fake = Faker()
        users = [fake.name() for _ in range(9)]
        users.insert(1, 'static_user')
        return users

    @pytest.fixture
    def individual_leaderboard(self):
        return LeaderboardViews('individual_rankings')

    @pytest.fixture
    def main_leaderboard(self):
        return LeaderboardViews('main_leaderboard')

    def test_add_user(self, redis, users, individual_leaderboard, main_leaderboard):
        # Add users to individual rankings with their main leaderboard ranking as the score
        for index, name in enumerate(users):
            main_leaderboard.add_user(name, index)

        # Adjust individual ranking scores after main leaderboard is fully populated 
        for user in users:
            individual_leaderboard._populate_individual_rankings(user)

        # Get the rank of the 'static_user' in the 'main_leaderboard'
        main_leaderboard_rank = redis.zrevrank('main_leaderboard', 'static_user')

        # The score of the 'static_user' in the 'individual_rankings' should be equal to their rank in the 'main_leaderboard'
        individual_ranking_score = redis.zscore('individual_rankings', 'static_user')

        # The score of the 'static_user' in the 'individual_rankings' should be equal to their rank in the 'main_leaderboard'
        assert individual_ranking_score == main_leaderboard_rank

    def test_should_update_individual_ranking_when_main_leaderboard_increases(self, redis, individual_leaderboard, main_leaderboard):
        # Get the initial score of a user ('static_user') in the individual leaderboard
        initial_ranking_score = redis.zscore('individual_rankings', 'static_user')

        # Define the number of spaces the user should move up in the leaderboard
        spaces_to_move = 5

        # Update the rank of the user in the main leaderboard by moving it up by 'spaces_to_move'
        main_leaderboard.update_user_rank_by_spaces('static_user', spaces_to_move)

        # Get the rank of the user in the main leaderboard after moving it
        main_leaderboard_rank = redis.zrevrank('main_leaderboard', 'static_user')

        # Get the final score of the user in the individual leaderboard after the update
        final_ranking_score = redis.zscore('individual_rankings', 'static_user')

        # Assert that the final score in the individual leaderboard equals the initial score minus the moved spaces
        # Also, assert that this final score equals the rank of the user in the main leaderboard
        assert final_ranking_score == initial_ranking_score - spaces_to_move == main_leaderboard_rank

class TestTeamLogic:
    @pytest.fixture(scope='class', autouse=True)
    def redis(self):
        conn = get_redis_connection('default')
        yield conn
        conn.flushall()

    @pytest.fixture
    def users(self):
        fake = Faker()
        users = [fake.name() for _ in range(98)]
        users.insert(0, 'team_member_A')
        users.insert(50, 'team_member_B')
        return users

    @pytest.fixture
    def individual_leaderboard(self):
        return LeaderboardViews('individual_rankings')

    @pytest.fixture
    def main_leaderboard(self):
        return LeaderboardViews('main_leaderboard')
    
    def test_should_create_with_highest_members_score(self, redis, main_leaderboard):
        