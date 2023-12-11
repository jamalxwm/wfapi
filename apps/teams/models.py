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
        return self._members

    @score.setter
    def score(self, score):
        self._score = score

    @rank.setter
    def rank(self, rank):
        self._rank = rank

    def start_team(self, members, rank, score):
        self._members.update(members)
        for member in members:
            member.join_team(self)
        self._rank = rank
        self._score = score

    def end_team(self):
        self._members.clear()
        