import unittest
from unittest.mock import MagicMock, patch
from .models import Team
from .manager import TeamsManager

class TestTeam(unittest.TestCase):
    def setUp(self):
        self.team = Team(team_id=1)
        self.mock_members = [MagicMock(), MagicMock()]

    def test_initialization(self):
        self.assertEqual(self.team.team_id, 1)
        self.assertEqual(self.team.score, 0)
        self.assertEqual(self.team.rank, 0)
        self.assertEqual(len(self.team.members), 0)

    def test_start_team(self):
        self.team.start_team(members=self.mock_members, rank=5, score=100)
        self.assertEqual(self.team.score, 100)
        self.assertEqual(self.team.rank, 5)
        self.assertEqual(self.team.members, set(self.mock_members))
        for mock_member in self.mock_members:
            mock_member.join_team.assert_called_once_with(self.team)

    def test_end_team(self):
        # Preparing the team with some members
        self.team.start_team(members=self.mock_members, rank=5, score=100)
        self.team.end_team()
        self.assertEqual(len(self.team.members), 0)

    def test_score_setter(self):
        self.team.score = 50
        self.assertEqual(self.team.score, 50)

    def test_rank_setter(self):
        self.team.rank = 3
        self.assertEqual(self.team.rank, 3)

class TestTeamsManager(unittest.TestCase):

    def setUp(self):
        # Mock the leaderboard object
        self.mock_leaderboard = MagicMock()
        self.teams_manager = TeamsManager(self.mock_leaderboard)

        # Mock user objects
        self.user1 = MagicMock()
        self.user1.user_id = 'user1'
        self.user1.team = None
        self.user1.rank = 500
        self.user1.score = 5

        self.user2 = MagicMock()
        self.user2.user_id = 'user2'
        self.user2.team = None
        self.user2.rank = 100
        self.user2.score = 500

        # Mock team object
        self.team = MagicMock()
        self.team.members = [self.user1, self.user2]
        self.team.team_id = 'user1_user2'
        self.team.score = 100
    
    def mock_get_rank_and_score(self, user_id):
        return (500, 5) if user_id == 'user1' else (100, 500)
    
    def test_validate_team_members_creates_team(self):
        with patch.object(TeamsManager, '_get_rank_and_score', side_effect=self.mock_get_rank_and_score):
            self.mock_leaderboard.get_user_rank_and_score.return_value = (1, 100)
            self.teams_manager.validate_team_members([self.user1, self.user2])
            created_team = next((team for team in self.teams_manager.teams if team.team_id == 'user1_user2'), None)
            self.assertIsNotNone(created_team)
            self.assertEqual(created_team.team_id, 'user1_user2')
            self.assertEqual(created_team.score, 500)
            self.assertEqual(len(self.teams_manager.teams), 1)

    def test_validate_team_members_raises_exception_for_teamed_user(self):
        self.user1.team = 'some_team'
        with self.assertRaises(Exception) as context:
            self.teams_manager.validate_team_members([self.user1, self.user2])
        self.assertIn('already in a team', str(context.exception))

    def test_validate_team_members_raises_exception_for_invalid_team_size(self):
        with self.assertRaises(Exception) as context:
            self.teams_manager.validate_team_members([self.user1])
        self.assertIn('Teams must consist of two users', str(context.exception))

    def test_disband_team(self):
        # Set up the team and add it to the TeamsManager
        self.user1.team = self.team
        self.user2.team = self.team
        self.teams_manager.teams.add(self.team)
        self.teams_manager.disband_team(self.user1)
        self.assertNotIn(self.team, self.teams_manager.teams)
        self.mock_leaderboard.remove_user.assert_called_with(self.team.team_id)
        self.team.end_team.assert_called_once()

    def test_team_id_creation(self):
        team_id = self.teams_manager._create_team_id([self.user1, self.user2])
        self.assertEqual(team_id, 'user1_user2')

    def test_add_and_remove_from_leaderboard(self):
        self.teams_manager._create_new_team(self.team)
        self.mock_leaderboard.add_user.assert_called_with(self.team.team_id, self.team.score)
        self.teams_manager._remove_team_from_lb(self.team)
        self.mock_leaderboard.remove_user.assert_called_with(self.team.team_id)

    def test_reinstate_team_members_to_lb(self):
        self.mock_leaderboard.get_score_at_rank.return_value = 50
        self.teams_manager._reinstate_team_members_to_lb(self.team)
        calls = [unittest.mock.call(self.user1.user_id, 50), unittest.mock.call(self.user2.user_id, 50)]
        self.mock_leaderboard.add_user.assert_has_calls(calls, any_order=True)


if __name__ == '__main__':
    unittest.main()