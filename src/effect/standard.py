from abc import ABC
from functools import total_ordering

from src.objects.character import Character

@total_ordering
class StandardEffect(ABC):
    """持续状态基类"""

    def __init__(self, name: str, duration: int, owner: Character):
        self.name = name
        self.duration = duration  # 剩余持续回合数
        self.owner = owner
        self.applied = False
        self.effective = True

    def on_apply(self):
        """状态被施加时触发一次"""
        if self.applied:
            return
        self.applied = True

    def on_turn_start(self):
        """拥有者回合开始时触发"""
        pass

    def on_action(self):
        """拥有者每次行动触发"""
        pass

    def on_turn_end(self):
        """拥有者回合结束时触发"""
        pass

    def on_remove(self):
        """状态被移除时触发"""
        pass

    def tick(self):
        """通用回合流逝逻辑：减少持续回合，返回是否已过期"""
        if self.duration <= 0:
            self.effective = False
            return
        self.duration -= 1

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        if not isinstance(other, StandardEffect):
            return NotImplemented
        return self.name < other.name