import arcade


class IllustrationManager:
    def __init__(self):
        self.is_combat = False

        self.team: list = []
        self.enemy: list = []
        self.team_illu = [
            {illu: arcade.Sprite(i.combat[illu], scale=0.1) for illu in ['normal', 'attack', 'low_health']} for i in
            self.team]
        self.team_illu_index = ['normal' for _ in self.team]
        self.enemy_illu = [
            {illu: arcade.Sprite(i.combat[illu], scale=0.1) for illu in ['normal', 'attack', 'low_health']} for i in
            self.enemy]
        self.enemy_illu_index = ['normal' for _ in self.enemy]

        self.delegate = []

    @property
    def combat(self):
        return self.is_combat
    @combat.setter
    def combat(self, value):
        self.is_combat = True
        self.team = value[0]
        self.enemy = value[1]
        self.team_illu = [{illu: arcade.Sprite(i.combat_illu[illu], scale=0.3) for illu in ['normal', 'attack', 'low_health']} for i in self.team]
        self.team_illu_index = ['normal' for _ in self.team]
        self.enemy_illu = [{illu: arcade.Sprite(i.combat_illu[illu], scale=0.3) for illu in ['normal', 'attack', 'low_health']} for i in self.enemy]
        self.enemy_illu_index = ['normal' for _ in self.enemy]
    @combat.deleter
    def combat(self):
        self.is_combat = False
        self.team = []
        self.enemy = []

    def change_illu(self, team: str, who, duration: float, change_to: str):
        if team == "no":
            t, id = self._find_char(who)
        else:
            t, id = team, who

        self.delegate.append({
            "team": t,
            "index": id,
            "timer": 0,
            "duration": duration,
            "illu": change_to
        })

    def _find_char(self, who):
        try:
            return "team", self.team.index(who)
        except:
            return "enemy", self.enemy.index(who)

    def update(self, delta_time: float):
        for i, char in enumerate(self.team):
            if char.hp < char.max_hp * 0.4:
                self.team_illu_index[i] = 'low_health'
            else:
                self.team_illu_index[i] = 'normal'
        for i, char in enumerate(self.enemy):
            if char.hp < char.max_hp * 0.4:
                self.enemy_illu_index[i] = 'low_health'
            else:
                self.enemy_illu_index[i] = 'normal'

        for d in self.delegate:
            d['timer'] += delta_time
            if d['team'] == "team":
                self.team_illu_index[d['index']] = d['illu']
            else:
                self.enemy_illu_index[d['index']] = d['illu']

            if d['timer'] >= d['duration']:
                self.delegate.remove(d)

    def get_illu(self, who):
        t, id = self._find_char(who)
        if t == 'team':
            return self.team_illu[id][self.team_illu_index[id]]
        else:
            return self.enemy_illu[id][self.enemy_illu_index[id]]

illu_manager = IllustrationManager()