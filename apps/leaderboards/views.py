from django_redis import get_redis_connection

class Leaderboard:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Leaderboard, cls).__new__(cls)
        return cls._instance

    def __init__(self, leaderboard, conn=None):
        self.leaderboard = leaderboard
        self.conn = conn if conn else get_redis_connection("default")
    
    
    def add_user(self, user, score):
        # Add the user to the main leaderboard
        self.conn.zadd(self.leaderboard, {user: score})

    def delete_user(self, user):
        self.conn.zrem(self.leaderboard, user)

    def get_user_rank(self, user):
        rank = self.conn.zrevrank(self.leaderboard, user)
        return rank if rank is not None else None
    
    def get_user_score(self, user):
        return self.conn.zscore(self.leaderboard, user)

    def increment_user_score(self, score, user):
        return self.conn.zincrby(self.leaderboard, score, user)

    def get_leaderboard_length(self):
        return self.conn.zcard(self.leaderboard)

    def get_user_by_rank(self, rank):
        return self.conn.zrevrange(self.leaderboard, rank, rank, withscores=True)

class SoloRanks:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SoloRanks, cls).__new__(cls)
        return cls._instance

    def __init__(self, solo_ranks, conn=None):
        self.solo_ranks = solo_ranks
        self.conn = conn if conn else get_redis_connection("default")

    def populate_solo_rankings(self, solo_user, user_rank):
        #user_rank_main = self.conn.zrevrank(main_leaderboard, user)
        if user_rank is not None:
            self.conn.hset(self.solo_ranks, solo_user, user_rank)
        else:
            raise Exception(f"Rank for user {solo_user} not found in main leaderboard.")

    def increment_user_rank(self, solo_user, spaces):
        current_rank = int(self.conn.hget(self.solo_ranks, solo_user))
        if current_rank - spaces < 0:
            spaces = current_rank
            
        return self.conn.hincrby(self.solo_ranks, solo_user, -spaces)



    # def update_user_rank_by_spaces(self, initiator, spaces):
    #     user = initiator
    #     is_team = self.conn.hexists('user_teams', initiator)

    #     if is_team:
    #         user = self._get_team_id(initiator)
  
    #     current_score = self.conn.zscore(self.leaderboard, user)
    #     current_rank = self.get_user_rank(user)

    #     if current_rank is None and not is_team:
    #         self.add_user(user, 0)
    #         self.update_user_rank_by_spaces(user, spaces)
    #         return

    #     target_rank = max(0, current_rank - spaces)
    #     self._increment_individual_rankings_by_spaces(initiator, spaces)
    #     return self._move_user_to_rank(user, current_score, target_rank)




    # def _move_user_to_rank(self, user, current_score, target_rank, skip_value=0.01):
    #     user_at_target_rank = self._get_user_by_rank(target_rank)

    #     # Look for next user on the leaderboard if none at target rank
    #     while not user_at_target_rank and target_rank < self.get_leaderboard_length():
    #         target_rank += 1
    #         user_at_target_rank = self._get_user_by_rank(target_rank)

    #     if user_at_target_rank:
    #         _, target_score = user_at_target_rank[0]
    #     else:
    #         target_score = current_score + 1  # Default score if no user at target rank

    #     new_score = target_score - current_score + skip_value
    #     self.conn.zincrby(self.leaderboard, new_score, user)

    #     return f"Moved {user} to rank {target_rank + 1}"

    # def _populate_individual_rankings(self, user):
    #         user_rank_main = self.conn.zrevrank('main_leaderboard', user)
            
    #         if user_rank_main is not None:
    #             self.conn.hset('individual_rankings', user, user_rank_main)
    #         else:
    #             print(f"Rank for user {user} not found in main leaderboard.")

    # def _increment_individual_rankings_by_spaces(self, user, spaces):
    #     return self.conn.hincrby('individual_rankings', user, -spaces)

    # def create_new_team(self, user1, user2):
    #     team_id = f'{user1}_{user2}'
        
    #     score1 = self.conn.zscore('main_leaderboard', user1)
    #     score2 = self.conn.zscore('main_leaderboard', user2)
        
    #     team_score = max(score1, score2) if score1 and score2 else score1 or score2

    #     self.conn.hset('user_teams', user1, team_id)
    #     self.conn.hset('user_teams', user2, team_id)
        
    #     self.conn.zrem('main_leaderboard', user1)
    #     self.conn.zrem('main_leaderboard', user2)

    #     return self.add_user(team_id, team_score)

    # def _get_team_id(self, user):
    #    return self.conn.hget('user_teams', user)

    # def delete_team(self, initiator):
    #     team_id = self._get_team_id(initiator)
    #     # Get the team ID to find both users
    #     # Find users final ranking in individual rankings
    #     # Reinstate users to main leaderboard to correct rank (use skip value 0)
    #     # Remove team from leaderboard and user_teams