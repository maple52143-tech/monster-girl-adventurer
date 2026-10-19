"""敌人的技能条目。

与玩家卡牌的区别：不看行动点、不入手牌、不弃牌，
但复用同一份卡牌数据（assets/data/card/*.json）与同一批效果类。
"""

from src.core.status_manager import status_manager
from src.objects.card import Card


class SkillEntry:
    def __init__(self, name: str, intention: str, owner):
        self.name = name
        self.intention = intention
        self.owner = owner
        # 复用卡牌数据解析（含效果类的解析），敌人不消耗这张卡
        self.card = Card(name, owner)

    # --- 兼容旧的字典式访问（skills[0]['intention'] / ['skill']）---
    def __getitem__(self, key):
        if key == 'skill':
            return self.card
        if key == 'intention':
            return self.intention
        raise KeyError(key)

    @staticmethod
    def _pick(side: str):
        """返回该阵营当前的目标；没有合法目标（全灭 / 指针越界）时返回 None。"""
        chars = status_manager.enemy if side == "enemy" else status_manager.team
        if not chars:
            return None
        ptr = status_manager.enemy_ptr if side == "enemy" else status_manager.team_ptr
        if not 0 <= ptr < len(chars):
            return None
        return chars[ptr]

    def valid_targets(self) -> bool:
        """技能所需的目标是否都还在（用于战斗结束时不再出手）。"""
        for _, _, target, _ in self.card.effects:
            if target in ("enemy", "team") and self._pick(target) is None:
                return False
        return True

    def cast(self) -> bool:
        """释放技能：不看行动点，只把效果挂到目标身上并立即结算。"""
        if not self.valid_targets():
            return False

        for cls, value, target, params in self.card.effects:
            who = self.owner if target == "self" else self._pick(target)
            if who is None:
                continue
            who.effects.append(cls(who, value, **params))

        status_manager.check_effect()
        for e in self.owner.effects:
            e.on_action()
        return True
