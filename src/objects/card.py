import arcade

from src.core.resource_manager import res_manager
from src.core.status_manager import status_manager
from src.core.illustration_manager import illu_manager

class Card(arcade.Sprite):
    def __init__(self, name: str, owner):
        t, self.data = res_manager.card(name)
        super().__init__(t, 0.13)

        self.owner = owner
        self.type = self.data['type']
        self.ap = self.data['action_point']
        self.effects = []
        for name, value in self.data['effect'].items():
            # value: [主数值, 目标] 或 [主数值, 目标, {额外的关键字参数}]
            params = value[2] if len(value) > 2 else {}
            self.effects.append((res_manager.effect(name), value[0], value[1], params))

        self.is_touched = False
        self.delegate = []
        self.ori_scale = 0.13
        self.curr_scale = self.ori_scale
        self.touch_scale = 0
        self.select_scale = 0

    def init(self):
        self.delegate = []
        self.scale = self.ori_scale

    def _pick_target(self, target: str):
        """取效果的目标；没有合法目标（例如敌人已全灭）时返回 None。"""
        if target == "self":
            return self.owner
        chars = status_manager.enemy if target == "enemy" else status_manager.team
        ptr = status_manager.enemy_ptr if target == "enemy" else status_manager.team_ptr
        if not chars or not (0 <= ptr < len(chars)):
            return None
        return chars[ptr]

    def valid_targets(self) -> bool:
        """这张卡需要的目标是否都还在。"""
        return all(self._pick_target(e[2]) is not None for e in self.effects)

    def use_card(self) -> bool:
        """打出这张卡。

        返回是否成功：行动点不足、或者需要的目标已经不存在（例如敌人全灭后
        还用攻击牌）时返回 False，由调用方决定怎么反馈。
        """
        if self.owner.action_point < self.ap:
            return False
        if not self.valid_targets():
            return False

        self.owner.action_point -= self.ap
        for e in self.effects:
            who = self._pick_target(e[2])
            if who is None:
                continue
            who.effects.append(e[0](who, e[1], **e[3]))
        status_manager.check_effect()
        for e in self.owner.effects:
            e.on_action()
        if self.type == "attack":
            illu_manager.change_illu("no", self.owner, 0.6, "attack")
        if self.owner.type == 'character':
            self.owner.hand.remove(self)
            self.owner.discard_pile.append(self)

        return True

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        self.curr_scale = self.ori_scale + self.touch_scale + self.select_scale
        if self.ori_scale - 0.02 <= self.curr_scale <= self.ori_scale + 0.07:
            self.scale = self.curr_scale
        else:
            self.curr_scale = self.ori_scale
            self.scale = self.curr_scale
        for d in self.delegate:
            if d.update(delta_time):
                self.delegate.remove(d)