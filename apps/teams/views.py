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

class Teams:
    def __init__(self, teams, conn=None):
        self.teams = teams
        self.conn = conn if conn else get_redis_connection("default")

    def get_team_id(self, user):
        return self.conn.hget(self.teams, f'{user}:team_id')
    
    def create_team_id(self, user1, user2):
        return f"{user1}_{user2}"

    def get_team_members(self, user):
        team_id = self.get_team_id(user)
        members = team_id.split('_')
        return members

class TeamUser:
    def __init__(self, user_id, teams, lb, ranking_manager conn=None):
        self.teams = teams
        self.user = user_id
        self.conn = conn if conn else get_redis_connection("default")
        self.ld = lb
        self.rm = ranking_manager

    def is_user_teamed(self):
        return self.conn.hexists(self.teams, self.user)

    def get_user_fallback_values(self):
        rank, score = self.conn.hmget(self.teams, [f'{self.user}:fallback_rank', f'{self.user}:fallback_score'])
        return rank, score

    def initialize_user_fallbacks(self):
        rank, score = self.get_user_lb_rank_score(self.user)
        mappings = { team_id: None,
                        fallback_rank: rank,
                        fallback_score: score, }
        return mappings

    def update_user_fallbacks(self, score, spaces):
        rank, score = self.get_user_fallback_values(self.user)
        if rank - spaces < 0:
            spaces = rank
        self.conn.hincrby(self.teams, f'{self.user}:fallback_rank', -spaces)
        self.conn.hincrbyfloat(self.teams, f'{self.user}:fallback_score', score)

    def restore_user_to_lb_rank(self, score, rank):
        # Restore user to their fallback rank
        rank, score = self.get_user_fallback_values(self.user)
        self.rm._move_user_to_rank(self.user, score, rank, skip_value=0)
    
    def restore_user_to_lb_score(self):
        # Restore user to their fallback score
        _, score = self.get_user_fallback_values(self.user)
        self.lb.add_user(self.user, score)
    
    def get_user_lb_rank_score(self):
        rank, score = self.lb.get_user_rank(self.user, withscores=True)
        return rank, score