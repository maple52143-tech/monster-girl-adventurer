import arcade

from src.objects.standard import StandardSet
from src.objects.character import Character
from src.core.illustration_manager import illu_manager

class CharacterBlock(StandardSet):

    def __init__(self, x, y, character: Character):
        super().__init__(x, y, "center", "center", (100, 100))
        self.character = character
        self.illu = illu_manager.get_illu(self.character)
        self.add_sprite(self.illu, 0, 0, 0)

    def update(self):
        self.change_sprite(self.illu, illu_manager.get_illu(self.character))
        self.illu = illu_manager.get_illu(self.character)
