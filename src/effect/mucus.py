from src.effect.standard import StandardEffect
from src.objects.character import Character
from src.objects.card import Card

class MucusEffect(StandardEffect):
    """粘液：拥有者被打到（护盾完全挡下不算）时，往手牌里塞牌。"""

    def __init__(self, owner: Character, layers: int = 1, duration: int = 100000):
        super().__init__("mucus", duration, owner)
        self.layers = max(0, int(layers))

    def on_enemy_turn_end(self):
        if not self.owner.is_hurt:
            return
        for _ in range(self.layers):
            self.owner.hand.append(Card('mucus', self.owner))
        self.owner.is_hurt = False
        self.effective = False


EFFECT_CLASS = MucusEffect
