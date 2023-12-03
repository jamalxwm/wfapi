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

    @pytest.mark.skip(reason="refactoring the leaderboard class")
    def test_update_user_position(self, redis, leaderboard):
        # Update user score and check if it's updated correctly
        start_position = leaderboard.get_user_rank(self.STATIC_USER)
        spaces_to_move = 5
        leaderboard.update_user_rank_by_spaces(self.STATIC_USER, spaces_to_move)

        assert redis.zrevrank('main_leaderboard', self.STATIC_USER) == start_position - spaces_to_move
    
    @pytest.mark.skip(reason="refactoring the leaderboard class")
    def test_update_user_position_if_negative_space_jumps(self, redis, leaderboard):
        # Update user score and check if it's updated correctly
        spaces_to_move = 20
        leaderboard.update_user_rank_by_spaces(self.STATIC_USER, spaces_to_move)

        assert redis.zrevrank('main_leaderboard', self.STATIC_USER) == 0

    def test_get_leaderboard_length(self, leaderboard):
        assert leaderboard.get_leaderboard_length() == self.NUM_USERS

    def test_delete_user(self, leaderboard):
        leaderboard.delete_user(self.STATIC_USER)
        assert leaderboard.get_leaderboard_length() == self.NUM_USERS - 1
        assert leaderboard.get_user_rank(self.STATIC_USER) is None


class TestSoloRanks:
    NUM_USERS = 10
    STATIC_USER = 'static_user'   
    INSERTION_POINT = 8
    NON_USER = 'non_user'

    @pytest.fixture(scope='class', autouse=True)
    def redis(self):
        conn = get_redis_connection('default')
        yield conn
        conn.flushall()

    @pytest.fixture
    def solo_ranks(request):
        solo_ranks = SoloRanks('solo_rankings')
        yield solo_ranks
        # After the test, reset the singleton instance to None
        type(solo_ranks)._instance = None

    @pytest.fixture
    def leaderboard(request):
        leaderboard = Leaderboard('main_leaderboard')
        yield leaderboard
        # After the test, reset the singleton instance to None
        type(leaderboard)._instance = None

    @pytest.fixture
    def users(self, leaderboard):
        fake = Faker()
        users = [fake.name() for _ in range(self.NUM_USERS - 1)]
        users.insert(self.INSERTION_POINT, self.STATIC_USER)

        for index, name in enumerate(users):
            leaderboard.add_user(name, index)

        return users

    def test_populate_solo_rankings_success(self, users, leaderboard, solo_ranks):
        for _, name in enumerate(users):
            rank = leaderboard.get_user_rank(name)
            solo_ranks.populate_solo_rankings(name, rank)
        
        assert solo_ranks.conn.hexists(solo_ranks.solo_ranks, self.STATIC_USER) is not None
        assert int(solo_ranks.conn.hget(solo_ranks.solo_ranks, self.STATIC_USER)) == max(0, self.NUM_USERS - self.INSERTION_POINT - 1)

    def test_populate_solo_rankings_failure(self, users, solo_ranks):
        with pytest.raises(Exception):
            solo_ranks.populate_solo_rankings(self.NON_USER, None)

    def test_increment_user_rank(self, users, solo_ranks):
        increment_value1 = 2
        static_user_start_rank = int(solo_ranks.conn.hget(solo_ranks.solo_ranks, self.STATIC_USER))
        solo_ranks.increment_user_rank(self.STATIC_USER, increment_value1)
        static_user_final_rank = int(solo_ranks.conn.hget(solo_ranks.solo_ranks, self.STATIC_USER))
    
        assert static_user_final_rank == max(0, static_user_start_rank - increment_value1)
        
    @pytest.mark.skip(reason="refactoring the leaderboard class")
    def test_add_user(self, redis, users, individual_leaderboard, main_leaderboard):
        # Add users to individual rankings with their main leaderboard ranking as the score
        for index, name in enumerate(users):
            main_leaderboard.add_user(name, index)

        # Adjust individual ranking scores after main leaderboard is fully populated 
        for user in users:
            individual_leaderboard._populate_individual_rankings(user)

        # Get the rank of the self.STATIC_USER in the 'main_leaderboard'
        main_leaderboard_rank = redis.zrevrank('main_leaderboard', self.STATIC_USER)

        # The score of the self.STATIC_USER in the 'individual_rankings' should be equal to their rank in the 'main_leaderboard'
        individual_ranking_score = redis.hget('individual_rankings', self.STATIC_USER)

        # The score of the self.STATIC_USER in the 'individual_rankings' should be equal to their rank in the 'main_leaderboard'
        assert int(individual_ranking_score) == main_leaderboard_rank
    @pytest.mark.skip(reason="refactoring the leaderboard class")
    def test_should_update_individual_ranking_when_main_leaderboard_increases(self, redis, individual_leaderboard, main_leaderboard):
        # Get the initial score of a user (self.STATIC_USER) in the individual leaderboard
        initial_ranking_score = redis.hget('individual_rankings', self.STATIC_USER)
        
        # Define the number of spaces the user should move up in the leaderboard
        spaces_to_move = 5

        # Update the rank of the user in the main leaderboard by moving it up by 'spaces_to_move'
        main_leaderboard.update_user_rank_by_spaces(self.STATIC_USER, spaces_to_move)

        # Get the rank of the user in the main leaderboard after moving it
        main_leaderboard_rank = redis.zrevrank('main_leaderboard', self.STATIC_USER)

        # Get the final score of the user in the individual leaderboard after the update
        final_ranking_score = redis.hget('individual_rankings', self.STATIC_USER)

        # Assert that the final score in the individual leaderboard equals the initial score minus the moved spaces
        # Also, assert that this final score equals the rank of the user in the main leaderboard
        assert int(final_ranking_score) == int(initial_ranking_score) - spaces_to_move == main_leaderboard_rank

class TestTeamLogic:
    @pytest.fixture(scope='class', autouse=True)
    def redis(self):
        conn = get_redis_connection('default')
        yield conn
        conn.flushall()

    @pytest.fixture(scope='class', autouse=True)
    def users(self):
        fake = Faker()
        users = [fake.name() for _ in range(98)]
        users.insert(0, 'team_member_A')
        users.insert(50, 'team_member_B')
        return users

    @pytest.fixture(scope='class', autouse=True)
    def individual_leaderboard(self):
        return LeaderboardViews('individual_rankings')

    @pytest.fixture(scope='class', autouse=True)
    def main_leaderboard(self):
        return LeaderboardViews('main_leaderboard')

    @pytest.fixture(scope='class', autouse=True)
    def seed_db(self, users, main_leaderboard, redis):
        for index, name in enumerate(users):
            main_leaderboard.add_user(name, index)
        
        leaderboard = redis.zrange('main_leaderboard', 0, -1, withscores=True)

        for user, _ in leaderboard:
            main_leaderboard._populate_individual_rankings(user)
         
    @pytest.mark.run(order=1)
    def test_should_create_with_highest_members_score(self, redis, main_leaderboard):
        score1 = redis.zscore('main_leaderboard', 'team_member_A')
        score2 = redis.zscore('main_leaderboard', 'team_member_B')
        main_leaderboard.create_new_team('team_member_A', 'team_member_B')
        
        assert redis.zscore('main_leaderboard', 'team_member_A_team_member_B') == max(score1, score2)
    
    @pytest.mark.run(order=2)
    def test_should_replace_team_members_with_team(self, redis):
        assert redis.zrevrank('main_leaderboard', 'team_member_A') == None
        assert redis.zrevrank('main_leaderboard', 'team_member_B') == None

    @pytest.mark.run(order=3)
    def test_should_add_team_members_to_team_hashset(self, redis):
        assert redis.hget('user_teams', 'team_member_A') != None
        assert redis.hget('user_teams', 'team_member_B') != None

    @pytest.fixture
    def leaderboard_setup(self, redis, main_leaderboard):
        team_start_rank = main_leaderboard.get_user_rank('team_member_A_team_member_B')
        spaces_to_move = 5
        initial_user_A_rank = redis.hget('individual_rankings', 'team_member_A')
        main_leaderboard.update_user_rank_by_spaces('team_member_A', spaces_to_move)
        team_final_rank = main_leaderboard.get_user_rank('team_member_A_team_member_B')
        return team_start_rank, spaces_to_move, team_final_rank, initial_user_A_rank

    @pytest.mark.run(order=4)
    def test_should_update_team_rank_on_leaderboard(self, leaderboard_setup, redis):
        team_start_rank, spaces_to_move, team_final_rank, _ = leaderboard_setup
        assert redis.zrevrank('main_leaderboard', 'team_member_A_team_member_B') == team_start_rank - spaces_to_move == team_final_rank

    def test_should_only_update_ranking_of_initiator(self, leaderboard_setup, redis, main_leaderboard):
        _, spaces_to_move, _, initial_user_A_rank = leaderboard_setup

        # Assert User A's rank on individual_rankings has updated by 5
        final_user_A_rank = int(redis.hget('individual_rankings', 'team_member_A'))
        assert final_user_A_rank == int(initial_user_A_rank) - spaces_to_move

        # Assert User B's rank on individual_rankings is unchanged
        initial_user_B_rank = redis.hget('individual_rankings', 'team_member_B')

        assert redis.hget('individual_rankings', 'team_member_B') == initial_user_B_rank

        # Assert user A and user B are not on the main leaderboard
        assert main_leaderboard.get_user_rank('team_member_A') is None
        assert main_leaderboard.get_user_rank('team_member_B') is None

    @pytest.mark.run(order=5)
    def test_should_reinstate_team_members_position(self, individual_leaderboard, main_leaderboard):
        main_leaderboard.delete_team('team_member_B')
        assert main_leaderboard.get_user_rank('team_member_A') == 94
        assert main_leaderboard.get_user_rank('team_member_B') == 49