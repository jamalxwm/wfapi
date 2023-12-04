import unittest
from unittest.mock import MagicMock, patch
from .views import TeamUser
from apps.leaderboard.views import Leaderboard

class TestTeamUser(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.lb = MagicMock()
        self.rm = MagicMock()
        self.teams = "teams"
        self.user_id = "user123"
        self.team_user = TeamUser(
            user_id=self.user_id,
            teams=self.teams,
            lb=self.lb,
            ranking_manager=self.rm,
            conn=self.conn
        )

    def test_is_user_teamed_exist(self):
        self.conn.hexists.return_value = 1

        self.assertTrue(self.team_user.is_user_teamed())

    def test_is_user_teamed_not_exist(self):
        self.conn.hexists.return_value = 0

        self.assertFalse(self.team_user.is_user_teamed())

    def test_get_user_fallback_values(self):
        self.conn.hmget.return_value = ["rank_mock", "score_mock"]

        rank, score = self.team_user.get_user_fallback_values()

        self.conn.hmget.assert_called_once_with(self.teams, [f'{self.user_id}:fallback_rank', f'{self.user_id}:fallback_score'])

        assert rank == "rank_mock"
        assert score == "score_mock"

    @patch.object(TeamUser, 'get_user_lb_rank_score')
    def test_initialize_user_fallbacks(self, mock_get_user_lb_rank_score):
        mock_get_user_lb_rank_score.return_value = ("mock_rank", "mock_score")

        result = self.team_user.initialize_user_fallbacks()

        mock_get_user_lb_rank_score.assert_called_once()

        expected_result = {
            "team_id": "",
            "fallback_rank": 'mock_rank',
            "fallback_score": 'mock_score'
        }
        
        assert result == expected_result

    @patch.object(TeamUser, 'get_user_fallback_values')
    def test_update_user_fallback_values(self, mock_get_user_fallback_values):
        CURR_SCORE = 101
        NEW_SCORE = 99.5
        CURR_RANK = 10
        SPACES = 5
        mock_get_user_fallback_values.return_value = (CURR_RANK, CURR_SCORE)

        self.team_user.update_user_fallbacks(NEW_SCORE, SPACES)

        mock_get_user_fallback_values.assert_called_once()
        self.conn.hincrby.assert_called_once_with(self.teams, f'{self.user_id}:fallback_rank, {-SPACES}')
        self.conn.hincrbyfloat.assert_called_once_with(self.teams, f'{self.user_id}:fallback_score, {NEW_SCORE}')

    @patch.object(TeamUser, 'get_user_fallback_values')
    def test_update_user_fallback_rank_below_zero(self, mock_get_user_fallback_values):
        CURR_SCORE = 101
        NEW_SCORE = 99.5
        CURR_RANK = 50
        SPACES = 300
        mock_get_user_fallback_values.return_value = (CURR_RANK, CURR_SCORE)

        self.team_user.update_user_fallbacks(NEW_SCORE, SPACES)

        mock_get_user_fallback_values.assert_called_once()
        self.conn.hincrby.assert_called_once_with(self.teams, f'{self.user_id}:fallback_rank, {-CURR_RANK}')
        self.conn.hincrbyfloat.assert_called_once_with(self.teams, f'{self.user_id}:fallback_score, {NEW_SCORE}')
    
    @patch.object(TeamUser, 'get_user_fallback_values')
    def test_restore_user_to_lb_rank(self, mock_get_user_fallback_values):
        RANK = 9
        SCORE = 101.5
        mock_get_user_fallback_values.return_value = (RANK, SCORE)

        self.team_user.restore_user_to_lb_rank()

        self.rm._move_user_to_rank.assert_called_once_with(self.user_id, SCORE, RANK, skip_value=0)
    
    @patch.object(TeamUser, 'get_user_fallback_values')
    def test_restore_user_to_lb_score(self, mock_get_user_fallback_values):
        RANK = 9
        SCORE = 101.5
        mock_get_user_fallback_values.return_value = (RANK, SCORE)

        self.team_user.restore_user_to_lb_score()

        self.lb.add_user.assert_called_once_with(self.user_id, SCORE)

    @patch.object(TeamUser, 'get_user_lb_rank_score')
    def test_get_user_lb_rank_score(self, mock_get_user_lb_rank_score):
        mock_get_user_lb_rank_score.return_value = ("mock_rank", "mock_score")

        rank, score = self.team_user.get_user_lb_rank_score()

        assert rank == "mock_rank"
        assert score =="mock_score"


class TeamsTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_get_redis_connection = patch('your_module.get_redis_connection').start()  # replace with the actual module
        self.mock_redis = MagicMock()
        self.mock_get_redis_connection.return_value = self.mock_redis
        self.teams_list = ['userA', 'userB']
        self.teams = Teams(self.teams_list, conn=self.mock_redis)

    def tearDown(self):
        patch.stopall()

    def test_init(self):
        self.assertEqual(self.teams.teams, self.teams_list)
        self.mock_get_redis_connection.assert_called_once_with('default')
        self.assertEqual(self.teams.conn, self.mock_redis)  

    def test_t
if __name__ == "__main__":
    unittest.main()