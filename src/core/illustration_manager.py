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
            if id is None:              # 不在名单里（例如已被移出战斗）就不播动画
                return
        else:
            t, id = team, who

        self.delegate.append({
            "team": t,
            "index": id,
            "char": who,          # 记录对象本身，列表重排时用它重映射索引
            "timer": 0,
            "duration": duration,
            "illu": change_to
        })

    def _find_char(self, who):
        for side, chars in (("team", self.team), ("enemy", self.enemy)):
            for i, c in enumerate(chars or ()):
                if c is who:
                    return side, i
        return None, None

    @staticmethod
    def _refresh_index(chars, illu_index):
        """按血量刷新默认立绘状态；长度不同步时只处理能对上的部分。"""
        for i, char in enumerate(chars):
            if i >= len(illu_index):
                break
            illu_index[i] = 'low_health' if char.hp < char.max_hp * 0.4 else 'normal'

    def attach(self, who, side: str = None):
        """把某个角色的立绘字典交给表现层直接持有，避免靠索引反查。

        返回 ``(illu_dict, key)``：``illu_dict`` 是 {normal/attack/low_health: Sprite}，
        ``key`` 是该角色当前状态的字符串。战斗列表缩短、索引前移都不会影响它。
        """
        if side is None:
            side, i = self._find_char(who)
            if i is None:
                return None, None
        else:
            chars = self.team if side == "team" else self.enemy
            i = next((n for n, c in enumerate(chars or ()) if c is who), None)
            if i is None:
                return None, None

        illu = self.team_illu if side == "team" else self.enemy_illu
        index = self.team_illu_index if side == "team" else self.enemy_illu_index
        if i >= len(illu):
            return None, None
        return illu[i], (index[i] if i < len(index) else 'normal')

    def sync(self, blocks):
        """把各动画的临时状态写到对应的表现对象上（每帧调用一次）。

        直接按角色对象匹配，索引怎么重排都不影响。
        """
        for b in blocks:
            illu, key = self.attach(b.character, b.illu_side)
            if illu is not None:
                b.illu_illu, b.illu_key = illu, key

    def _prune_side(self, side: str, alive: list):
        """把某一侧的立绘表按存活名单重排。

        单位被移出列表后索引会整体前移，如果不同步重排，
        ``_find_char`` 返回的新索引会落到别的角色（甚至是已倒下的角色）的立绘上，
        表现就是“打掉一个之后剩下的敌人不再播出手动画”。
        """
        illu_attr = "team_illu" if side == "team" else "enemy_illu"
        index_attr = "team_illu_index" if side == "team" else "enemy_illu_index"
        old_chars = list(self.team if side == "team" else self.enemy) or []
        old_illu = getattr(self, illu_attr)
        old_index = getattr(self, index_attr)

        old_pos = {id(c): i for i, c in enumerate(old_chars)}

        new_illu, new_index = [], []
        for c in alive:
            i = old_pos.get(id(c))
            if i is None or i >= len(old_illu):
                continue
            new_illu.append(old_illu[i])
            new_index.append(old_index[i] if i < len(old_index) else 'normal')
        setattr(self, illu_attr, new_illu)
        setattr(self, index_attr, new_index)

        # 动画按角色对象重映射；角色已离场就直接丢掉
        new_pos = {id(c): i for i, c in enumerate(alive)}
        for d in tuple(self.delegate):
            if d['team'] != side:
                continue
            new_i = new_pos.get(id(d.get('char')))
            if new_i is None:
                self.delegate.remove(d)
            else:
                d['index'] = new_i

    def remove_dead(self, team: list, enemy: list):
        """按存活名单重排立绘与动画索引。调用方负责把传入的列表也更新掉。"""
        self._prune_side("team", team)
        self._prune_side("enemy", enemy)
        self.team = team
        self.enemy = enemy

    def update(self, delta_time: float):
        self._refresh_index(self.team, self.team_illu_index)
        self._refresh_index(self.enemy, self.enemy_illu_index)

        for d in tuple(self.delegate):
            d['timer'] += delta_time
            if d['team'] == "team":
                self.team_illu_index[d['index']] = d['illu']
            else:
                self.enemy_illu_index[d['index']] = d['illu']

            if d['timer'] >= d['duration']:
                self.delegate.remove(d)

    def get_illu(self, who):
        illu, key = self.attach(who)
        if illu is None:
            return None
        return illu[key]


illu_manager = IllustrationManager()