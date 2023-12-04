from django_redis import get_redis_connection
from leaderboards.views import Leaderboard as lb
from leaderboards.manager import RankingManager

class TeamsManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Teams, cls).__new__(cls)
        return cls._instance

    def __init__(self, teams, lb, teamuser, conn=None):
        self.teams = teams
        self.lb = lb
        self.conn = conn if conn else get_redis_connection("default")
        self.teamuser = teamuser
        self.teams = teams

    def setup_team(self, users):
        self.check_users_not_teamed(users)
        self.check_team_is_duo(users)
        team_id = self.teams.create_team_id(*users)

        user_mappings = []
        # Get both users score and ranks
        for user in users:
            initial_fallback_values = self.teamuser.initialize_user_fallbacks(user)
            initial_fallback_values[user].team_id = team_id
            user_mappings.append({user: initial_fallback_values})
        
        # Initialise the team with the highest user's score
        team_start_score = max(user_mappings[users[0]].fallback_score, user_mappings[users[1]].fallback_score)
        
        self.create_new_team(user_mappings, team_id, users, team_start_score)
    
    
    def create_new_team(self, user_mappings, team_id, users, team_score):
      # Add team members to hashset with initial fallback values
        for mapping in user_mappings:
            self.conn.hset(self.teams, mapping)
        
        # Remove the team members from the leaderboard
        self.lb.delete_user(*users)
        # Add the team to the leaderboard
        self.lb.add_user(team_id, team_score)

    def check_users_not_teamed(self, users):
        if any(self.teamuser.is_user_teamed(user) for user in [users]):
            raise Exception('User already in a team')

    def check_team_is_duo(self, users):
        if len(users) != 2:
            raise Exception('Teams must be two users')
        
    def disband_team(self, initiator):
        team_id = self.get_team_id(initiator)
        users = team_id.split('_')
        # Get the users fallback value and use one of the two methods to restor them to the leaderboard
        for user in users:
            [fallback_rank, fallback_score] = self.teamuser.get_user_fallback_values(user)
            self.teamuser.restore_user_to_lb_rank(user, fallback_score, fallback_rank)
        
        self.delete_team(team_id, users)
    
    def delete_team(self, team, users):
        #remove the team members from the hash set
        self.conn.hdel(self.teams, *users)
        # Remove the team from the leadeboard
        self.lb.delete_user(team)
