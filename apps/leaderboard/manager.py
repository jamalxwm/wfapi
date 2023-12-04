from .views import Leaderboard, SoloRanks
from teams.views import teams

class RankingManager:
    def __init__(self, leaderboard, teams, solo_ranks):
        self.leaderboard = Leaderboard(leaderboard)
        self.teams = Teams(teams)
        self.solo_ranks = SoloRanks(solo_ranks)

    def update_user_rank_by_spaces(self, initiator, spaces):
        user = initiator
        is_team = self.teams.is_user_teamed(initiator)

        if is_team:
            user = self.teams.get_team_id(initiator)
  
        current_score = self.leaderboard.get_user_score(user)
        current_rank = self.leaderboard.get_user_rank(user)

        if current_rank is None and not is_team:
            self.leaderboard.add_user(user, 0)
            self.update_user_rank_by_spaces(user, spaces)
            return

        target_rank = max(0, current_rank - spaces)

        self.solo_ranks.increment_user_rank(initiator, spaces)
        return self._move_user_to_rank(user, current_score, target_rank)

    def _move_user_to_rank(self, user, current_score, target_rank, skip_value=0.01):
        user_at_target_rank = self.leaderboard.get_user_by_rank(target_rank)

        # Look for next user on the leaderboard if none at target rank
        while not user_at_target_rank and target_rank < self.leaderboard.get_leaderboard_length():
            target_rank += 1
            user_at_target_rank = self.leaderboard._get_user_by_rank(target_rank)

        if user_at_target_rank:
            _, target_score = user_at_target_rank[0]
        else:
            target_score = current_score + 1  # Default score if no user at target rank

        new_score = target_score - current_score + skip_value
        self.leaderboard.increment_user_score(new_score, user)

        return f"Moved {user} to rank {target_rank + 1}"