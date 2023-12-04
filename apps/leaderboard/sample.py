import redis

r = redis.Redis()

# Assuming `user1` and `user2` are the users forming a team
team_id = user1 + "_" + user2  # form a unique team_id

# find the score of both users in the individual leaderboard
score1 = r.zscore('individual_scores', user1)
score2 = r.zscore('individual_scores', user2)

team_score = max(score1, score2) if score1 and score2 else score1 or score2

# add the team to the main leaderboard
r.zadd('main_leaderboard', {team_id: team_score})

# add an entry in the user_teams hash for each user
r.hset('user_teams', user1, team_id)
r.hset('user_teams', user2, team_id)

# When a user leaves the team

# get the team_id from the user_teams hash
team_id = r.hget('user_teams', user1)

# remove the team from the leaderboard
r.zrem('main_leaderboard', team_id)

# remove the user from the team in user_teams hash
r.hdel('user_teams', user1)

# get the user's individual score
score = r.zscore('individual_scores', user1)

# re-add the user to the main leaderboard with their individual score
r.zadd('main_leaderboard', {user1: score})

from django_redis import get_redis_connection







class IndividualRankings:

    def __init__(self, conn=None):
        self.conn = conn if conn else get_redis_connection("default")

    def _populate_individual_rankings(self, user, main_leaderboard):
        user_rank_main = self.conn.zrevrank(main_leaderboard, user)
        if user_rank_main is not None:
            self.conn.hset('individual_rankings', user, user_rank_main)
        else:
            print(f"Rank for user {user} not found in main leaderboard.")

    def _increment_individual_rankings_by_spaces(self, user, spaces):
        return self.conn.hincrby('individual_rankings', user, -spaces)