from django_redis import get_redis_connection

class Teams:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Teams, cls).__new__(cls)
        return cls._instance

    def __init__(self, teams, conn=None):
        self.teams = teams
        self.conn = conn if conn else get_redis_connection("default")

    def create_new_team(self, user1, user2, team_score):
        team_id = f'{user1}_{user2}'
        self.conn.hset(self.teams, user1, team_id)
        self.conn.hset(self.teams, user2, team_id)
        return team_id, team_score

    def get_team_id(self, user):
       return self.conn.hget(self.teams, user)

    def delete_team(self, initiator):
        team_id = self.get_team_id(initiator)
        users = team_id.split('_')
        self.conn.hdel(self.teams, *users)
        return users  # return deleted users for further processing
   
    def is_user_teamed(self, user):
        return self.conn.hexists(self.teams, user)
    # get max score for create team
    # add team to leaderboard and side effects
    # remove team from leaderboard and side effects when reinstating users use 0 for skip value