from django_redis import get_redis_connection


class Leaderboards:
    conn = get_redis_connection("default")

    @staticmethod
    def add_user(user, score):
        Leaderboards.conn.zadd('leaderboard', {user: score})

    @staticmethod
    def delete_user(user):
        Leaderboards.conn.zrem('leaderboard', user)

    @staticmethod
    def update_user_rank_by_spaces(user, spaces):
        current_score = Leaderboards.conn.zscore('leaderboard', user)
        current_rank = Leaderboards.get_user_rank(user) - 1
        
        if current_rank is None:
            Leaderboards.add_user(user, 0)
            Leaderboards.update_user_rank_by_spaces(user, spaces)
        
        target_rank = max(0, current_rank - spaces)
        return Leaderboards._move_user_to_rank(user, current_score, target_rank)
    
    @staticmethod
    def get_user_rank(user):
        return Leaderboards.conn.zrevrank('leaderboard', user) + 1
    
    @staticmethod
    def get_leaderboard_length():
        return Leaderboards.conn.zcard('leaderboard')
    
    @staticmethod
    def _get_user_by_rank(rank):
        return Leaderboards.conn.zrevrange('leaderboard', rank, rank, withscores=True)
    
    @staticmethod
    def _move_user_to_rank(user, current_score, target_rank):
        user_at_target_rank = Leaderboards._get_user_by_rank(target_rank)
        target_score = current_score + 0.01 # Default score if no user at target rank

        if user_at_target_rank:
            _, target_score = user_at_target_rank[0]

        new_score = target_score - current_score + 0.01
        Leaderboards.conn.zincrby('leaderboard', new_score, user)

        return f"Moved {user} to rank {target_rank + 1}"
   