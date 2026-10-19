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

    @staticmethod
    def _alive_index(chars, current: int) -> int:
        """把指针挪到最近的存活单位；全都死了或列表为空时回落到 0。"""
        if not chars:
            return 0
        current %= len(chars)
        for offset in range(len(chars)):
            i = (current + offset) % len(chars)
            if not chars[i].death:
                return i
        return 0

    def update_ptr(self):
        self._team_pointer = self._alive_index(self.team, self._team_pointer)
        self._enemy_pointer = self._alive_index(self.enemy, self._enemy_pointer)

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

    @staticmethod
    def _run_effects(target, hook_name: str):
        """在快照上遍历效果，避免边遍历边删除漏掉相邻元素。"""
        for e in tuple(target.effects):
            getattr(e, hook_name)()
            if not e.effective:
                target.effects.remove(e)
                e.on_remove()

    def _group(self, who: str):
        return self.team if who == "team" else self.enemy

    def check_effect(self):
        for t in tuple(self.team):
            self._run_effects(t, "on_apply")
        for t in tuple(self.enemy):
            self._run_effects(t, "on_apply")

    def on_turn_start(self, who: str):
        for t in tuple(self._group(who)):
            self._run_effects(t, "on_turn_start")
        if who == "team":
            # 本回合是否挨打已经结算过了，清掉标记，避免下一回合误触发
            for t in tuple(self.team):
                t.is_hurt = False

    def on_turn_end(self, who: str):
        for t in tuple(self._group(who)):
            self._run_effects(t, "on_turn_end")
        if who == "enemy":
            # 敌方回合结束时，队伍身上的“被攻击触发”类状态也要结算
            for t in tuple(self.team):
                self._run_effects(t, "on_enemy_turn_end")


status_manager = StatusManager()
