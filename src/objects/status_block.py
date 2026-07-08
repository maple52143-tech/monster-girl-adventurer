import arcade

from src.objects.standard import StandardSet
from src.objects.character import Character
from src.core.resource_manager import res_manager


class StatusBlock(StandardSet):
    def __init__(self, x: float, y: float, character: Character):
        super().__init__(x, y, "left", "top", (300, 60))

        self.avatar = arcade.Sprite(character.avatar, scale=0.05)
        self.add_sprite(self.avatar, self.avatar.width / 2, self.size[1] / 2)

        self.select = arcade.Sprite(res_manager.image("choose_corner"), 0.1)
        self.add_sprite(self.select, self.select.width / 2, self.size[1] - self.select.height / 2)

        self.hp_bar = arcade.Sprite(res_manager.image("hp_bar"), 0.1)
        self.hp_bar_shield = arcade.Sprite(res_manager.image("hp_bar_shield"), 0.1)
        self.add_sprite(self.hp_bar, 120 + self.hp_bar.width / 2, self.size[1] / 2)
        self.add_sprite(self.hp_bar_shield, 120 + self.hp_bar.width / 2, self.size[1] / 2)

        self.character = character
        self.is_chosen = True

    def update(self):
        self.hp_bar_shield.visible = True if self.character.shield > 0 else False
        self.select.visible = self.is_chosen