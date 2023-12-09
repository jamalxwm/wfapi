from django_redis import get_redis_connection
from .models import Teams, TeamUser
class TeamsManager:

    def __init__(self, teams, teamuser, conn=None):
        self.teams = teams
        self.teamuser = teamuser
        self.conn = conn if conn else get_redis_connection("default")
        self.MAX_TEAM_SIZE = 2

    def validate_team_members(self, users):
        self._check_users_not_teamed(users)
        self._check_team_is_pair(users)
        team_id = self.teams.create_team_id(*users)
        return users, team_id
    
    def setup_team(self, users, team_id):
        user_mappings = []
        # Get both users score and ranks
        for user in users:
            initial_fallback_values = self.teamuser.initialize_user_fallbacks(user)
            initial_fallback_values[user].team_id = team_id
            user_mappings.append({user: initial_fallback_values})
        
        userA_score, userB_score = user_mappings[users[0]].fallback_score, user_mappings[users[1]].fallback_score
        # Initialise the team with the highest user's score
        team_start_score = max(userA_score, userB_score)
        
        self._create_new_team(user_mappings, team_id, users, team_start_score) 
    
    def _create_new_team(self, user_mappings, team_id, users, team_score):
      # Add team members to hashset with initial fallback values
        self.teams.add_team_members_to_hashset(user_mappings)
        
        # Remove the team members from the leaderboard
        for team_user in users:
            self.teamuser.remove_team_user_from_lb(team_user)
        # Add the team to the leaderboard
        self.teams.add_new_team_to_lb(team_id, team_score)
        
    def disband_team(self, initiator):
        team_id = self.teams.get_team_id(initiator)
        users = team_id.split('_')
        # Get the users fallback value and use one of the two methods to restor them to the leaderboard
        for user in users:
            [fallback_rank, fallback_score] = self.teamuser.get_user_fallback_values(user)
            self.teamuser.restore_user_to_lb_rank(user, fallback_score, fallback_rank)
        
        self.delete_team(team_id, users)
    
    def delete_team(self, team, users):
        #remove the team members from the hash set
        self.teams.remove_team_members_from_hashset(*users)
        # Remove the team from the leadeboard
        self.teams.remove_team_from_lb(team)

    def _check_users_not_teamed(self, users):
        if any(self.teamuser.is_user_teamed(user) for user in [users]):
            raise Exception('User already in a team')

    def _check_team_is_pair(self, users):
        if len(users) != self.MAX_TEAM_SIZE:
            raise Exception('Teams must be two users')
    
    @classmethod
    def load_teams(cls):
        pass