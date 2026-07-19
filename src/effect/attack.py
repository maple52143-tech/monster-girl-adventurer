from src.effect.standard import StandardEffect
from src.objects.character import Character

class AttackEffect(StandardEffect):
    def __init__(self, owner: Character, damage: float = 6.0):
        super().__init__("attack", 0, owner)
        self.damage = damage

    def on_apply(self):
        super().on_apply()
        self.owner.hp = self.owner.hp - self.damage
        self.tick()