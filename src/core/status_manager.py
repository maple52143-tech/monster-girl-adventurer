

class StatusManager:
    def __init__(self):
        self.is_combat = False

        self.team: list = None
        self.enemy: list = None
        self._team_pointer = 0
        self._enemy_pointer = 0

    @property
    def combat(self):
        return self.is_combat
    @combat.setter
    def combat(self, value):
        self.is_combat = True
        self.team = value[0]
        self.enemy = value[1]
    @combat.deleter
    def combat(self):
        self.is_combat = False
        self.team = None
        self.enemy = None

    @property
    def team_ptr(self):
        return self._team_pointer
    @team_ptr.setter
    def team_ptr(self, value: int):
        if value >= 4:
            raise ValueError(f"这里站不下这么多人: {value}")
        self._team_pointer = value

    @property
    def enemy_ptr(self):
        return self._enemy_pointer
    @enemy_ptr.setter
    def enemy_ptr(self, value: int):
        if value >= 4:
            raise ValueError(f"这里站不下这么多敌人: {value}")
        self._enemy_pointer = value

    def _find_char(self, who):
        try:
            return "team", self.team.index(who)
        except:
            return "enemy", self.enemy.index(who)

    def get_character(self, who):
        t, id = self._find_char(who)
        if t == 'team':
            return self.team[id]
        else:
            return self.enemy[id]

    def check_effect(self):
        for t in self.team:
            for e in t.effects:
                e.on_apply()
                if not e.effective:
                    t.effects.remove(e)
        for t in self.enemy:
            for e in t.effects:
                e.on_apply()
                if not e.effective:
                    t.effects.remove(e)

    def on_turn_start(self, who: str):
        match who:
            case "team":
                k = self.team
            case "enemy":
                k = self.enemy
        for t in k:
            for e in t.effects:
                e.on_turn_start()
                if not e.effective:
                    t.effects.remove(e)

    def on_turn_end(self, who: str):
        match who:
            case "team":
                k = self.team
            case "enemy":
                k = self.enemy
        for t in k:
            for e in t.effects:
                e.on_turn_end()
                if not e.effective:
                    t.effects.remove(e)

status_manager = StatusManager()