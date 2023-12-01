from django_redis import get_redis_connection


class Leaderboards:

    def __init__(self, leaderboard, conn=None):
        self.leaderboard = leaderboard
        self.conn = conn if conn else get_redis_connection("default")

    def add_user(self, user, score):
        # Add the user to the main leaderboard
        self.conn.zadd('main_leaderboard', {user: score})

    def delete_user(self, user):
        self.conn.zrem(self.leaderboard, user)

    def update_user_rank_by_spaces(self, user, spaces):
        current_score = self.conn.zscore(self.leaderboard, user)
        current_rank = self.get_user_rank(user) - 1

        if current_rank is None:
            self.add_user(user, 0)
            self.update_user_rank_by_spaces(user, spaces)

        target_rank = max(0, current_rank - spaces)
        self._update_individual_rankings(user, target_rank)
        return self._move_user_to_rank(user, current_score, target_rank)

    def get_user_rank(self, user):
        rank = self.conn.zrevrank(self.leaderboard, user)
        return rank + 1 if rank is not None else None

    def get_leaderboard_length(self):
        return self.conn.zcard(self.leaderboard)

    def _get_user_by_rank(self, rank):
        return self.conn.zrevrange(self.leaderboard, rank, rank, withscores=True)

    def _move_user_to_rank(self, user, current_score, target_rank):
        user_at_target_rank = self._get_user_by_rank(target_rank)

        # Look for next user on the leaderboard if none at target rank
        while not user_at_target_rank and target_rank < self.get_leaderboard_length():
            target_rank += 1
            user_at_target_rank = self._get_user_by_rank(target_rank)

        if user_at_target_rank:
            _, target_score = user_at_target_rank[0]
        else:
            target_score = current_score + 1  # Default score if no user at target rank

        new_score = target_score - current_score + 0.01
        self.conn.zincrby(self.leaderboard, new_score, user)

        return f"Moved {user} to rank {target_rank + 1}"

    def _populate_individual_rankings(self, user):
            user_rank_main = self.conn.zrevrank('main_leaderboard', user)
            
            if user_rank_main is not None:
                self.conn.zadd('individual_rankings', {user: user_rank_main})
            else:
                print(f"Rank for user {user} not found in main leaderboard.")

    def _update_individual_rankings(self, user, new_rank):
        return self.conn.zadd('individual_rankings', {user: new_rank})

    def create_new_team(self, user1, user2):
        team_id = f'{user1}_{user2}'
        
        score1 = self.conn.zscore('main_leaderboard', user1)
        score2 = self.conn.zscore('main_leaderboard', user2)
        
        team_score = max(score1, score2) if score1 and score2 else score1 or score2
        
        self.conn.zrem('main_leaderboard', user1)
        self.conn.zrem('main_leaderboard', user2)

        return self.add_user(team_id, team_score)
