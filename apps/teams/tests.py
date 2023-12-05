import unittest
from unittest.mock import MagicMock, patch
from .views import TeamUser, Teams
from .manager import TeamsManager

class TestTeamUserCase(unittest.TestCase):
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
        self.conn = MagicMock()
        self.lb = MagicMock()
        self.teams_dict = {'userA': {'team_id': 'userA_userB,'}}
        self.teams = Teams(self.teams_dict, lb=self.lb, conn=self.conn)

    def tearDown(self):
        patch.stopall()
    
    def test_init(self):
        teams = Teams(self.teams_dict)

    def test_get_team_id(self):
        self.conn.hget.return_value = 'userA_userB'
        user = 'userA'

        result = self.teams.get_team_id(user)

        self.conn.hget.assert_called_once_with(self.teams_dict, 'userA:team_id')
        self.assertEqual(result, 'userA_userB')


    def test_create_team_id(self):
        result = self.teams.create_team_id('userA', 'userB')

        self.assertEqual(result, 'userA_userB')
    
    @patch.object(Teams, 'get_team_id')
    def test_get_team_members(self, mock_get_team_id):
        mock_get_team_id.return_value = 'userA_userB'
        user = 'userA'
        result = self.teams.get_team_members(user)
        self.teams.get_team_id.assert_called_once_with(user)

        assert result == ['userA', 'userB']

def TestTeamsManagerCase(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.teams = teams
        self.teamuser = teamuser
        #self.MAX_TEAM_SIZE = 2
        self.teamsmanager = TeamsManager(
            teams=self.teams,
            teamuser=self.teamuser
            conn=self.conn
        )

    def test_validate_team
if __name__ == "__main__":
    unittest.main()