from .models import Leaderboard

class RankingManager:
    def __init__(self, leaderboard):
        self.leaderboard = leaderboard

    def update_user_rank_by_spaces(self, initiator, spaces):
        player_id = initiator.team_id if initiator.team else initiator.user_id
        
        # Use leaderboard as source of truth for ranks and scores
        current_score = self.leaderboard.get_player_score(player_id)
        current_rank = self.leaderboard.get_player_rank(player_id)

        if current_rank is None and not initiator.team:
            self.leaderboard.add_player(player_id, initiator.score)
            self.update_user_rank_by_spaces(initiator, spaces)
            return

        target_rank = max(0, current_rank - spaces)

        new_score = self._calculate_points_to_rank(target_rank)
        
        if new_score is None:
            new_score = current_score + 1

        self._update_players_instance_values(initiator, spaces, target_rank, new_score)
        self._update_players_leaderboard_score(player_id, new_score)

    def _update_players_leaderboard_score(self, player_id, new_score):
        self.leaderboard.update_player_score(player_id, new_score)

    def _calculate_points_to_rank(self, target_rank):
        target_score = self.leaderboard.get_score_at_rank(target_rank)

        return target_score + 0.01 if target_score else None

    def _update_players_instance_values(self, initiator, spaces, target_rank, new_score):
        rank_update = {"rank": target_rank, "spaces": spaces}
        initiator.rank = rank_update
        initiator.score = new_score

        if initiator.team:
            team = initiator.team
            team.rank = target_rank
            team.score = new_score
