from django_redis import get_redis_connection

class Leaderboard:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Leaderboard, cls).__new__(cls)
        return cls._instance

    def __init__(self, conn=None):
        self.leaderboard = 'main_leaderboard'
        self.conn = conn if conn else get_redis_connection("default")
    
    def add_user(self, user, score):
        # Add the user to the main leaderboard
        self.conn.zadd(self.leaderboard, {user: score})

    def delete_user(self, user):
        self.conn.zrem(self.leaderboard, user)

    def get_user_rank(self, user, withscores=False):
        rank = self.conn.zrevrank(self.leaderboard, user, withscores)
        return rank if rank is not None else None
    
    def get_user_score(self, user):
        return self.conn.zscore(self.leaderboard, user)

    def increment_user_score(self, score, user):
        return self.conn.zincrby(self.leaderboard, score, user)

    def get_leaderboard_length(self):
        return self.conn.zcard(self.leaderboard)

    def get_user_by_rank(self, rank):
        return self.conn.zrevrange(self.leaderboard, rank, rank, withscores=True)
