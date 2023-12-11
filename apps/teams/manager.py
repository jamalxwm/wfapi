from django_redis import get_redis_connection
from .models import Team

class TeamsManager:

    def __init__(self, leaderboard):
        self.teams = set()
        self.leaderboard = leaderboard
        self.MAX_TEAM_SIZE = 2

    def validate_team_members(self, users):
        self._check_users_not_teamed(users)
        self._check_team_is_pair(users)
        
        self._inititalize_team_values(users) 

    def _inititalize_team_values(self, users):
        ranks_and_scores = [self._get_rank_and_score(user.user_id) for user in users]
        initial_rank, initial_score = max(ranks_and_scores, key=lambda x: x[1])

        team_id = self._create_team_id(users)
        
        new_team = Team(team_id)
        new_team.start_team(users, initial_rank, initial_score)

        self._create_new_team(new_team) 
    
    def _create_new_team(self, team):
        self.teams.add(team)

        self._add_team_to_lb(team)

        self._remove_team_members_from_lb(team)
       
    def disband_team(self, initiator):
        team = initiator.team
        self._reinstate_team_members_to_lb(team)
        self._remove_team_from_lb(team)
        team.end_team()
        self.teams.remove(team)
        
        
    def _create_team_id(self, users):
        return f"{users[0].user_id}_{users[1].user_id}"

    def _check_users_not_teamed(self, users):
        if any(user.team for user in users):
            raise Exception('One or more users are already in a team')

    def _check_team_is_pair(self, users):
        if len(users) != self.MAX_TEAM_SIZE:
            raise Exception('Teams must consist of two users')
    
    @classmethod
    def load_teams(cls):
        pass

    def _get_rank_and_score(self, user_id):
        return self.leaderboard.get_user_rank(user_id, withscores=True)
    
    def _remove_team_members_from_lb(self, team):
        for member in team.members:
            self.leaderboard.remove_user(member.user_id)
    
    def _add_team_to_lb(self, team):
        self.leaderboard.add_user(team.team_id, team.score)

    def _remove_team_from_lb(self, team):
        self.leaderboard.remove_user(team.team_id)

    def _reinstate_team_members_to_lb(self, team):
        for member in team.members:
            target_score = self.leaderboard.get_score_at_rank(member.rank)
            if not target_score:
                target_score = team.score / 2
            member.leave_team(target_score)
            self.leaderboard.add_user(member.user_id, target_score)
    
    