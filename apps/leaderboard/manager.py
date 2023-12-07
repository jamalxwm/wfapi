from .models import Leaderboard
# from apps.teams.models import Teams, TeamUser

class RankingManager:
    def __init__(self, leaderboard, teams):
        self.leaderboard = Leaderboard(leaderboard)
        self.teams = teams
        

    def update_user_rank_by_spaces(self, initiator, spaces):
        user = initiator.team_id if initiator.team_id else initiator.user_id

        if is_team:
            user = self.teams.get_team_id(initiator)
  
        current_score = initiator.score
        current_rank = initiator.rank

        if current_rank is None and not is_team:
            self.leaderboard.add_user(user, 0)
            self.update_user_rank_by_spaces(user, spaces)
            return

        target_rank = max(0, current_rank - spaces)

        initiator.rank -= spaces
        return self._move_user_to_rank(user, current_score, target_rank)

    def _move_user_to_rank(self, user, current_score, target_rank, is_restore=False):
       

        incr_value = self._calculate_increment_value(is_restore, target_score, current_score)
        self.leaderboard.increment_user_score(incr_value, user)

        return f"Moved {user} to rank {target_rank + 1}"

    def _calculate_increment_value(self, is_restore, target_score, current_score):
        if is_restore:
            incr_value = target_score
        else:
            incr_value = target_score - current_score + 0.01
        
        return incr_value

    
       