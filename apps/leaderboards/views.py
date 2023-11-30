from django_redis import get_redis_connection


class Leaderboards:
    conn = get_redis_connection("default")

    @staticmethod
    def add_user(user, score):
        Leaderboards.conn.zadd('leaderboard', {user: score})

    @staticmethod
    def update_user_position(user, spaces):
        current_rank = Leaderboards.conn.zrevrank('leaderboard', user)
        if current_rank is None:
            return 'User not found in leaderboard'
        
        target_rank = current_rank - spaces
        if target_rank < 0:
            return 'Cannot move user ahead by the given spaces'
            
        user_at_target_rank = Leaderboards.conn.zrange('leaderboard', target_rank, target_rank, withscores=True)
        if user_at_target_rank:
            _, target_score = user_at_target_rank[0]
            Leaderboards.add_user(user, target_score + 0.01)
            return f"Moved {user} ahead by {spaces} spaces to rank {target_rank + 1}"
        else:
            return 'No user found at this rank'


    @staticmethod
    def print_leaderboard():
        leaderboard = Leaderboards.conn.zrevrange('leaderboard', 0, -1, withscores=True)

        print('Leaderboard:', leaderboard)