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

    def add_player(self, player_id, score=None):
        # Add the player to the main leaderboard
        score = score or 0 #Default value
        self.conn.zadd(self.leaderboard, {player_id:score})

    def delete_player(self, player_id):
        self.conn.zrem(self.leaderboard, player_id)

    def get_player_rank(self, player_id, withscores=False):
        rank = self.conn.zrevrank(self.leaderboard, player_id, withscores)
        return rank if rank is not None else None
    
    def get_player_score(self, player_id):
        return self.conn.zscore(self.leaderboard, player_id)

    def increment_player_score(self, score, player_id):
        return self.conn.zincrby(self.leaderboard, score, player_id)

    def get_player_by_rank(self, rank):
        return self.conn.zrevrange(self.leaderboard, rank, rank, withscores=True)

    def get_score_at_rank(self, rank):
        _, score = None, None

        while not score and rank < self.length:
            _, score = self.get_player_by_rank(rank)[0]
            rank += 1
        
        return score if score else None

    def update_player_score(self, player_id, new_score):
        self.conn.zadd(self.leaderboard, {player_id: new_score}, xx=True)

    
class Player:
    def __init__(self, user_id):
        self.user_id = user_id
        self._score = 0.0
        self._rank = 0
        self._team = None

    @property
    def score(self):
        return self._score

    @score.setter  
    def score(self, score):
        if self._team:
            return
        else:
            self._score = score

    @property
    def rank(self):
        return self._rank
    
    @rank.setter
    def rank(self, rank_update):
        if self._team:
            self._rank = max(0, self._rank - rank_update['spaces']) 
        else:
            self._rank = max(0, rank_update['rank'])
    @property
    def team(self):
        return self._team if self._team else None
    
    @property
    def team_id(self):
        return self._team.team_id if self._team else None
 
    @property
    def teammate_id(self):
        if not self._team:
            return None
        for member in self._team.members:
            if member.user_id != self.user_id:
                return member.user_id

    def join_team(self, team):
        if self._team:
            raise Exception('This player is already on a team') 

        self._team = team
    
    def leave_team(self, score):
        if self._team:
            self._score = score
            self._team = None
        else:
            raise Exception('This player is not on a team')