from src.effect.standard import StandardEffect
from src.objects.character import Character

class DefenseEffect(StandardEffect):
    def __init__(self, owner: Character, defense: float = 5.0):
        super().__init__("defense", 0, owner)
        self.defense = defense

    def on_apply(self):
        super().on_apply()
        self.owner.shield += self.defense
        self.tick()