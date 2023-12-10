from django_redis import get_redis_connection

class Team:
    def __init__(self, team_id):
        self.team_id = team_id
        self._members = set()
        self._score = 0
        self._rank = 0

    @property
    def score(self):
        return self._score

    @property
    def rank(self):
        return self._rank

    @property
    def members(self):
        return self._members.objects.all()

    @score.setter
    def score(self, score):
        self._score = score

    @rank.setter
    def score(self, rank):
        self._rank = rank

    def start_team(self, members, rank, score):
        self._members.add(member for member in members)
        for member in members:
            member.join_team(self)
        self._rank = rank
        self._score = score

    def end_team(self):
        for member in self._members:
            self._members.discard(member)
        
class TeamsManager:

    def __init__(self, leaderboard):
        self.teams = set()
        self.leaderboard = leaderboard
        self.MAX_TEAM_SIZE = 2

    def validate_team_members(self, users):
        self._check_users_not_teamed(users)
        self._check_team_is_pair(users)
        
        self._inititalize_team_values(users) 

    def _inititalize_team_values(self, users):
        ranks_and_scores = [self._get_rank_and_score(user.user_id) for user in users]
        initial_rank, initial_score = max(ranks_and_scores, key=lambda x: x[1])

        team_id = self.create_team_id(users)
        
        new_team = Team(team_id)
        new_team.start_team(users, initial_rank, initial_score)

        self._create_new_team(new_team) 
    
    def _create_new_team(self, team):
        self.teams.append(team)

        self._add_team_to_lb(team)

        self._remove_team_members_from_lb(team)
       
    def disband_team(self, initiator):
        team = initiator.team
        self._reinstate_team_members_to_lb(team)
        self._remove_team_from_lb(team)
        team.end_team()
        self.teams.remove(team)
        
        
    def _create_team_id(self, users):
        return f"{users[0].user_id}_{users[1].user_id}"

    def _check_users_not_teamed(self, users):
        if any(user.team_id for user in [users]):
            raise Exception('User already in a team')

    def _check_team_is_pair(self, users):
        if len(users) != self.MAX_TEAM_SIZE:
            raise Exception('Teams must be two users')
    
    @classmethod
    def load_teams(cls):
        pass

    def get_rank_and_score(self, user_id):
        return self.leaderboard.get_user_rank(user_id, withscores=True)
    
    def _remove_team_members_from_lb(self, team):
        for member in team.members:
            self.leaderboard.remove_user(member.user_id)
    
    def _add_team_to_lb(self, team):
        self.leaderboard.add_user(team.team_id, team.score)

    def _remove_team_from_lb(self, team):
        self.leaderboard.remove_user(team.team_id)

    def _reinstate_team_members_to_lb(self, team):
        for member in team.members:
            target_score = self.leaderboard.get_score_at_rank(member.rank)
            member.leave_team(target_score)
            self.leaderboard.add_user(member.user_id, target_score)
    
    