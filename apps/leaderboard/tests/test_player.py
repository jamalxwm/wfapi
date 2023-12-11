import pytest
from unittest.mock import MagicMock
from apps.leaderboard.models import Player

class TestplayerCase:

    @pytest.fixture(scope='class', autouse=True)
    def player(self):
        return Player("John Doe")

    @pytest.fixture(scope='class', autouse=True)
    def mock_team(self):
        team = MagicMock()
        team.team_id = 'team1'
        return team

    def test_create_new_player(self, player):
        assert player.user_id == "John Doe"
        assert player.score == 0.0
        assert player.rank == 0
        assert player.team_id == None
        assert player.teammate_id == None

    def test_update_score(self, player):
        player.score = 50.0
        assert player.score == 50.0

    def test_update_rank(self, player):
        rank_update = {'rank' : 100, 'spaces': 5}
        player.rank = rank_update
        assert player.rank == 100

    def test_player_rank_does_not_surpass_zero(self, player):
        rank_update = {'rank' : 75, 'spaces': 5}
        player.rank = rank_update
        assert player.rank == 75

    def test_cannot_leave_team_when_not_on_one(self, player):
        with pytest.raises(Exception):
            player.leave_team()

    def test_join_team(self, player, mock_team):
        player.join_team(mock_team)
        assert player.team_id == 'team1'
    
    def test_team_players_rank_decrements_by_spaces(self, player):
        rank_update = {'rank' : 75, 'spaces': 10}
        player.rank = rank_update
        assert player.rank == 65

    def test_players_score_dont_update_while_on_team(self, player):
        NEW_SCORE = 200
        player.score = NEW_SCORE

        assert player.score == 50

    def test_cannot_join_team_when_on_one(self, player):
        with pytest.raises(Exception):
            player.join_team('team2', 'Joe Bloggs')

    def test_leave_team(self, player):
        NEW_SCORE = 505
        player.leave_team(NEW_SCORE)

        assert player.team_id == None
        assert player.score == NEW_SCORE

    def test_join_team_unknown_error(self, player):
        player._team_id = 'team3'

        with pytest.raises(Exception):
            player.join_team('team1', 'Jane Doe')
       
    def test_join_team_unknown_error(self, player):
        player._team_id = 'team3'

        with pytest.raises(Exception):
            player.leave_team()

