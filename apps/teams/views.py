from django_redis import get_redis_connection
from leaderboards.views import Leaderboards
from leaderboards.manager import RankingManager

class TeamsManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Teams, cls).__new__(cls)
        return cls._instance

    def __init__(self, teams, leaderboard, conn=None):
        self.teams = teams
        self.conn = conn if conn else get_redis_connection("default")

    def assemble_team(self, user1, user2):
        # Get both users score and ranks
        user1_rank, user2_rank = leaderboards.get_user_rank(user1), leaderboards.get_user_rank(user2)
        user1_score, user2_score = leaderboards.get_user_score(user1), leaderboards.get_user_score(user2)

        # Initialise the team with the highest user's score
        team_start_score = max(user1_start_score, user2_start_score)
        return self.create_new_team(user1, user2, user1_rank, user2_rank, user1_score, user2_score, team_start_score)
    
    def create_new_team(self, user1, user2, user1_rank, user2_rank, user1_score, user2_score, team_score):
        team_id = f'{user1}_{user2}'

        # Add team members to hashset with initial fallback values
        self.conn.hset(self.teams, user1, mapping={
            "team_id": team_id,
            "fallback_rank": user1_rank,
            "fallback_score": user1_score,
        })
        self.conn.hset(self.teams, user2, mapping={
            "team_id": team_id,
            "fallback_rank": user2_rank,
            "fallback_score": user2_score,
        })
        # Remove the team members from the leaderboard
        leaderboards.delete_user([user1, user2])
        # Add the team to the leaderboard
        return leaderboards.add_user(team_id, team_score)

    def get_team_id(self, user):
       return self.conn.hget(self.teams, user)

    def get_user_fallback_values(self, user):
        return self.conn.hmget(self.teams, [user + ":fallback_rank", user + ":fallback_score"])

    def update_user_fallbacks(self, user, score, spaces):
        rank, score = self.get_user_fallback_values(user)
        if rank - spaces < 0:
            spaces = rank
        self.conn.hincrbyfloat(self.teams, f'{user}:fallback_score', score)
        self.conn.hincrby(self.teams, f'{user}:fallback_rank', -spaces)
    
    def disassemble_team(self, initiator):
        team_id = self.get_team_id(initiator)
        users = team_id.split('_')
        # Get the users fallback value and use one of the two methods to restor them to the leaderboard
        for user in users:
            [fallback_rank, fallback_score] = self.get_user_fallback_values(user)
            RankingManager.move_user_to_rank(user)
        return self.delete_team(team_id, users)
    
    

    def delete_team(self, team, users):
        #remove the team members from the hash set
        self.conn.hdel(self.teams, *users)
        # Remove the team from the leadeboard
        leaderboard.delete_user(team)
   
   # The two methods below are different logics for restoring solo users after they've quit a team
   # I'm not sure which one is best yet, the first feels fairer to the user while the latter is more adherent to the rules
   # I'd like to simulate gameplay with a bigger leaderboard to figure it out
    def restore_user_to_leaderboard(self, user, rank):
        # put the user back at the rank they would have been at if they hadn't teamed
        return RankingManager._move_user_to_rank(user, fallback_score, fallback_rank, skip_value=0)
    
    def restore_user_to_leaderboard_alt(self, user, score):
        # put the user back at the right place for their score
        leaderboards.add_user(user, score)
   
    def is_user_teamed(self, user):
        return self.conn.hexists(self.teams, user)

    # add team to leaderboard and side effects
    # remove team from leaderboard and side effects when reinstating users use 0 for skip value

    class TeamUser:
        def __init__(self, name, id):