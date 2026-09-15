import math

from src.effect.standard import StandardEffect
from src.objects.character import Character
from src.objects.card import Card

class MucusEffect(StandardEffect):
    def __init__(self, owner: Character, t):
        super().__init__("mucus", 100000, owner)

    def on_enemy_turn_end(self):
        if self.owner.is_hurt:
            self.owner.hand.append(Card('mucus', self.owner))
            self.owner.is_hurt = False
            self.effective = False
