import unittest
from unittest.mock import MagicMock, patch
from apps.leaderboard.manager import RankingManager
from apps.leaderboard.models import Leaderboard


class TestRankingManager(unittest.TestCase):
    def setUp(self):
        # Mock the Leaderboard and TeamsManager
        self.mock_leaderboard = Leaderboard()
        self.mock_teams_manager = MagicMock()

        mock_team = MagicMock()
        mock_team.rank = 75
        mock_team.score = 100

        self.mock_teams_manager.load_teams.return_value = {456: mock_team}
        self.update_player_score_patch = patch.object(
            self.mock_leaderboard, "update_player_score"
        )

        
        # Patch the Leaderboard and TeamsManager
        teams_manager_patch = patch(
            "apps.teams.manager.TeamsManager", self.mock_teams_manager
        )
        self.mock_update_player_score = self.update_player_score_patch.start()
        self.addCleanup(self.update_player_score_patch.stop)
        # Start patching
        self.addCleanup(teams_manager_patch.stop)
        teams_manager_patch.start()

        # Patch the 'get_player_score' method
        self.get_player_score_patch = patch.object(
            self.mock_leaderboard, 'get_player_score', autospec=True
        )
        self.mock_get_player_score = self.get_player_score_patch.start()
        self.addCleanup(self.get_player_score_patch.stop)

        # Patch the 'get_player_rank' method
        self.get_player_rank_patch = patch.object(
            self.mock_leaderboard, 'get_player_rank', autospec=True
        )
        self.mock_get_player_rank = self.get_player_rank_patch.start()
        self.addCleanup(self.get_player_rank_patch.stop)

        # Patch the 'get_score_at_rank' method
        self.get_score_at_rank_patch = patch.object(
            self.mock_leaderboard, 'get_score_at_rank', autospec=True
        )
        self.mock_get_score_at_rank = self.get_score_at_rank_patch.start()
        self.addCleanup(self.get_score_at_rank_patch.stop)
        # Initialize the RankingManager with the mocked leaderboard and teams manager
        self.ranking_manager = RankingManager(
            self.mock_leaderboard, self.mock_teams_manager
        )
        self._update_players_leaderboard_score_patch = patch.object(
            self.ranking_manager, "_update_players_leaderboard_score", autospec=True
        )
        self.mock_update_players_leaderboard_score = (
            self._update_players_leaderboard_score_patch.start()
        )
        self.addCleanup(self._update_players_leaderboard_score_patch.stop)

    def test_update_user_rank_by_spaces_for_individual_user(self):
        # Arrange
        initiator = MagicMock()
        initiator.team_id = None
        initiator.user_id = 1
        initiator.score = 100
        initiator.rank = 90

        self.mock_leaderboard.get_player_score.return_value = initiator.score
        self.mock_leaderboard.get_player_rank.return_value = initiator.rank
        self.mock_leaderboard.get_score_at_rank.return_value = 101

        spaces = 10
        expected_new_rank = 80
        expected_new_score = (
            101.05  # This would be determined by the logic in _calculate_points_to_rank
        )

        self.ranking_manager._calculate_points_to_rank = MagicMock(
            return_value=expected_new_score
        )
        # Act
        self.ranking_manager.update_user_rank_by_spaces(initiator, spaces)
        
        # Assert
        self.ranking_manager._calculate_points_to_rank.assert_called_once()
        self.ranking_manager._update_players_leaderboard_score.assert_called_once_with(
            initiator.user_id, expected_new_score
        )
        
        # Add more assertions as needed to confirm that the rank and score are updated correctly

    # Add more test methods to cover different cases like team updates, edge cases, etc.
    def tearDown(self):
        self.mock_update_player_score.reset_mock()

    def test_update_user_rank_by_spaces_for_team_user(self):
        # Arrange
        initiator = MagicMock()
        initiator.team_id = 456
        initiator.user_id = 2
        initiator.score = 100
        initiator.rank = 90

        team = self.mock_teams_manager.load_teams.return_value[initiator.team_id]
        self.mock_leaderboard.get_player_score.return_value = team.score
        self.mock_leaderboard.get_player_rank.return_value = team.rank
        self.mock_leaderboard.get_score_at_rank.return_value = 101

        spaces = 10
        expected_new_rank = 80
        expected_new_score = (
            105  # This would be determined by the logic in _calculate_points_to_rank
        )

        self.ranking_manager._calculate_points_to_rank = MagicMock(
            return_value=expected_new_score
        )
        # Act
        self.ranking_manager.update_user_rank_by_spaces(initiator, spaces)
        
        # Assert
        self.ranking_manager._calculate_points_to_rank.assert_called_once()
        self.ranking_manager._update_players_leaderboard_score.assert_called_once_with(
            initiator.team_id, expected_new_score
        )



if __name__ == "__main__":
    unittest.main()
