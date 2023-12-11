import unittest
from unittest.mock import MagicMock, patch
from apps.leaderboard.manager import RankingManager
from apps.leaderboard.models import Leaderboard


class TestRankingManager(unittest.TestCase):
    
    def setUp(self):
        self.mock_get_redis_connection = patch('apps.leaderboard.models.get_redis_connection')
        self.mock_redis_conn = self.mock_get_redis_connection.start()
        self.mock_redis_instance = MagicMock()
        self.mock_redis_conn.return_value = self.mock_redis_instance
        self.mock_leaderboard = Leaderboard()

        self.update_player_score_patch = patch.object(
            self.mock_leaderboard, "update_player_score"
        )

        self.mock_update_player_score = self.update_player_score_patch.start()
        self.addCleanup(self.update_player_score_patch.stop)
        # Start patching

        # Patch the 'get_player_score' method
        self.get_player_score_patch = patch.object(
            self.mock_leaderboard, "get_player_score", autospec=True
        )
        self.mock_get_player_score = self.get_player_score_patch.start()
        self.addCleanup(self.get_player_score_patch.stop)

        # Patch the 'get_player_rank' method
        self.get_player_rank_patch = patch.object(
            self.mock_leaderboard, "get_player_rank", autospec=True
        )
        
        self.mock_get_player_rank = self.get_player_rank_patch.start()
        self.addCleanup(self.get_player_rank_patch.stop)

        self.add_player_patch = patch.object(
            self.mock_leaderboard, "add_player", autospec=True
        )
        self.mock_add_player = self.add_player_patch.start()
        self.addCleanup(self.add_player_patch.stop)

        # Patch the 'get_score_at_rank' method
        self.get_score_at_rank_patch = patch.object(
            self.mock_leaderboard, "get_score_at_rank", autospec=True
        )
        self.mock_get_score_at_rank = self.get_score_at_rank_patch.start()
        self.addCleanup(self.get_score_at_rank_patch.stop)
        # Initialize the RankingManager with the mocked leaderboard and teams manager
        self.ranking_manager = RankingManager(self.mock_leaderboard)
        self._update_players_leaderboard_score_patch = patch.object(
            self.ranking_manager, "_update_players_leaderboard_score", autospec=True
        )
        self.mock_update_players_leaderboard_score = (
            self._update_players_leaderboard_score_patch.start()
        )
        self.addCleanup(self._update_players_leaderboard_score_patch.stop)

    def test_update_user_rank_by_spaces_for_solo_player(self):
        # Arrange
        initiator = MagicMock()
        initiator.team = None
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

    def tearDown(self):
        self.mock_update_player_score.reset_mock()

    def test_update_user_rank_by_spaces_for_team_player(self):
        # Arrange
        team = MagicMock()
        team.team_id = "team1"
        team.score = 500
        team.rank = 50

        initiator = MagicMock()
        initiator.team = team
        initiator.team_id = team.team_id
        initiator.user_id = 2
        initiator.score = 100
        initiator.rank = 90

        self.mock_leaderboard.get_player_score.return_value = initiator.team.score
        self.mock_leaderboard.get_player_rank.return_value = initiator.team.rank
        self.mock_leaderboard.get_score_at_rank.return_value = 101

        spaces = 10
        expected_new_rank = team.rank - spaces
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

        assert team.score == expected_new_score
        assert team.rank == expected_new_rank

    def tearDown(self):
        self.mock_get_redis_connection.stop()

    def test_solo_player_not_on_leaderboard(self):
        # Arrange
        initiator = MagicMock()
        initiator.team = None
        initiator.user_id = 3
        initiator.score = 100
        initiator.rank = 90

        self.mock_leaderboard.get_player_score.return_value = None
        self.mock_leaderboard.get_player_rank.side_effect = [None, 80]
        
        def add_player_side_effect(player_id, score):
            # When add_player is called, get_player_score should return the score
            self.mock_leaderboard.get_player_score.return_value = score
            # Simulate that the player now has a rank
            self.mock_leaderboard.get_player_rank.return_value = 90

        # Assign the side effect function to add_player
        self.mock_leaderboard.add_player.side_effect = add_player_side_effect

        spaces = 10
        expected_new_rank = initiator.rank - spaces
        expected_new_score = (
            200  # This would be determined by the logic in _calculate_points_to_rank
        )

        self.ranking_manager._calculate_points_to_rank = MagicMock(
            return_value=expected_new_score
        )
        # Act
        self.ranking_manager.update_user_rank_by_spaces(initiator, spaces)
       
        # Assert
        self.mock_add_player.assert_called_once_with(initiator.user_id, 100)


if __name__ == "__main__":
    unittest.main()
