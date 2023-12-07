from django.db import models
from django_redis import get_redis_connection
from apps.leaderboard.models import Leaderboard as lb
from apps.leaderboard.manager import RankingManager

class Teams:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Teams, cls).__new__(cls)
        return cls._instance

    def __init__(self, lb, conn=None):
        self.teams = 'teams_hashset'
        self.lb = lb
        self.conn = conn if conn else get_redis_connection("default")

    def get_team_id(self, user):
        return self.conn.hget(self.teams, f'{user}:team_id')
    
    def create_team_id(self, user1, user2):
        return f"{user1}_{user2}"

    def get_team_members(self, user):
        team_id = self.get_team_id(user)
        members = team_id.split('_')
        return members

    def add_new_team_to_lb(self, team_id, init_score):
        self.lb.add_user(team_id, init_score)

    def remove_team_from_lb(self, team_id):
        self.lb.delete_user(team_id)

    def add_team_members_to_hashset(self, team_mappings):
        for team_member in team_mappings:
            self.conn.hset(self.teams, team_member)
    
    def remove_team_members_from_hashset(self, *team_members):
        self.conn.hdel(self.teams, team_members)

class TeamUser:
    def __init__(self, user_id, teams, lb, ranking_manager, conn=None):
        self.teams = teams
        self.user = user_id
        self.conn = conn if conn else get_redis_connection("default")
        self.lb = lb
        self.rm = ranking_manager

    def is_user_teamed(self):
        return self.conn.hexists(self.teams, self.user)

    def get_user_fallback_values(self):
        rank, score = self.conn.hmget(self.teams, [f'{self.user}:fallback_rank', f'{self.user}:fallback_score'])
        return rank, score

    def initialize_user_fallbacks(self):
        rank, score = self.get_user_lb_rank_score(self.user)
        mappings = { 
                     "team_id": "",
                     "fallback_rank": rank,
                     "fallback_score": score, 
                     }
        return mappings

    def update_user_fallbacks(self, score, spaces_to_decrement):
        rank, _ = self.get_user_fallback_values(self.user)
        if rank - spaces_to_decrement < 0:
            spaces_to_decrement = rank
        self.conn.hincrby(self.teams, f'{self.user}:fallback_rank, {-spaces_to_decrement}')
        self.conn.hincrbyfloat(self.teams, f'{self.user}:fallback_score, {score}')

    def remove_team_user_from_lb(self):
        self.lb.delete_user(self.user)
    
    def restore_user_to_lb_rank(self):
        # Restore user to their fallback rank
        rank, score = self.get_user_fallback_values(self.user)
        self.rm._move_user_to_rank(self.user, score, rank, is_restore=True)
    
    def restore_user_to_lb_score(self):
        # Restore user to their fallback score
        _, score = self.get_user_fallback_values(self.user)
        self.lb.add_user(self.user, score)
    
    def get_user_lb_rank_score(self):
        rank, score = self.lb.get_user_rank(self.user, withscores=True)
        return rank, score
