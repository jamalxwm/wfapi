from django_redis import get_redis_connection
from leaderboards.views import Leaderboard as lb
from leaderboards.manager import RankingManager

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