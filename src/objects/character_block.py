import arcade

from src.objects.standard import StandardSet
from src.objects.character import Character
from src.core.illustration_manager import illu_manager
from src.core.resource_manager import res_manager


class CharacterBlock(StandardSet):

    def __init__(self, x, y, character: Character):
        super().__init__(x, y, "left", "bottom", (200, 200))
        self.character = character
        self.sprites.add_sprite_list("intention")
        self.illu = illu_manager.get_illu(self.character)
        self.add_sprite(self.illu, 0, 0, 0)
        self.inten = {k: arcade.Sprite(res_manager.image(k, "intention"), 0.07) for k in
                      ['attack', 'defense', 'magic', 'move']}

    def update(self):
        self.change_sprite(self.illu, illu_manager.get_illu(self.character))
        self.illu = illu_manager.get_illu(self.character)

        if self.character.intention is not None:
            self.sprites['intention'].clear()
            inten = self.inten[self.character.intention]
            self.add_sprite(inten, 0, 200, list_name="intention")

