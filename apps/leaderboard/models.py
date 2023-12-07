from django.db import models
from django_redis import get_redis_connection

class Leaderboard:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Leaderboard, cls).__new__(cls)
        return cls._instance

    def __init__(self, conn=None):
        self.leaderboard = 'leaderboard'
        self.conn = conn if conn else get_redis_connection("default")
        self._length = self.conn.zcard(self.leaderboard)

    @property
    def length(self):
        return self._length

    def add_user(self, user, score=None):
        # Add the user to the main leaderboard
        score = score or 0 #Default value
        self.conn.zadd(self.leaderboard, {user:score})

    def delete_user(self, user):
        self.conn.zrem(self.leaderboard, user)

    def get_user_rank(self, user, withscores=False):
        rank = self.conn.zrevrank(self.leaderboard, user, withscores)
        return rank if rank is not None else None
    
    def get_user_score(self, user):
        return self.conn.zscore(self.leaderboard, user)

    def increment_user_score(self, score, user):
        return self.conn.zincrby(self.leaderboard, score, user)

    def get_user_by_rank(self, rank):
        return self.conn.zrevrange(self.leaderboard, rank, rank, withscores=True)

    def get_score_at_rank(self, rank):
        _, score = None, None

        while not score and rank < self.length:
            _, score = self.get_user_by_rank(rank)[0]
            rank += 1
        
        return score if score else None
class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self._score = 0.0
        self._rank = 0
        self._team_id = None
        self._teammate_id = None

    @property
    def score(self):
        return self._score

    @score.setter  
    def score(self, score):
        self._score = score

    @property
    def rank(self):
        return self._rank
    
    @rank.setter
    def rank(self, rank):
        self._rank = max(0, rank)

    @property
    def team_id(self):
        return self._team_id

    @property
    def teammate_id(self):
        return self._teammate_id

    def join_team(self, team_id, teammate_id):
        if self.team_id and self.teammate_id:
            raise Exception('This user is already on a team') 

        if bool(self.team_id) ^ bool(self.teammate_id):
            raise Exception('Unknown error. Please contact admin') 

        self._team_id = team_id
        self._teammate_id = teammate_id
    
    def leave_team(self):
        if not self.team_id and not self.teammate_id:
            raise Exception('This user is not on a team')

        if bool(self.team_id) ^ bool(self.teammate_id):
            raise Exception('Unknown error. Please contact admin') 

        self._team_id = None
        self._teammate_id = None