import arcade

from src.objects.standard import StandardSet
from src.objects.character import Character
from src.core.resource_manager import res_manager


class StatusBlock(StandardSet):
    def __init__(self, x: float, y: float, character: Character):
        avatar_size = 84
        hp_bar_size = 0.15
        super().__init__(x, y, "left", "top", (300, avatar_size))

        self.avatar = arcade.Sprite(character.avatar, scale=0.07)
        self.add_sprite(self.avatar, self.avatar.width / 2, self.avatar.height / 2)

        self.select = arcade.Sprite(res_manager.image("choose_corner"), 0.1)
        self.add_sprite(self.select, self.select.width / 2, self.size[1] - self.select.height / 2)

        self.hp_bar = arcade.Sprite(res_manager.image("hp_bar"), hp_bar_size)
        self.hp_bar_shield = arcade.Sprite(res_manager.image("hp_bar_shield"), hp_bar_size)
        self.add_sprite(self.hp_bar, avatar_size + self.hp_bar.width / 2, self.size[1] / 2)
        self.add_sprite(self.hp_bar_shield, avatar_size + self.hp_bar.width / 2, self.size[1] / 2)
        self.sprites.add_sprite_list_before("bar", "default")
        ori_topleft = (185, 153)
        ori_bottomright = (1055, 103)
        self.bar = arcade.SpriteSolidColor(int(870 * hp_bar_size), int(50 * hp_bar_size), color=arcade.csscolor.RED)
        self.add_sprite(self.bar, avatar_size + self.bar.width / 2 + 185 * hp_bar_size,
                        self.size[1] / 2, 0, "bar")
        self.hp_bar_size = hp_bar_size
        self.avatar_size = avatar_size

        self.character = character
        self.is_chosen = True

    def update(self):
        self.hp_bar_shield.visible = True if self.character.shield > 0 else False
        self.select.visible = self.is_chosen
        self.bar.width = 870 * self.hp_bar_size * (self.character.hp / self.character.max_hp)
        self.parts[self._find_sprite(self.bar)][1] = self.avatar_size + self.bar.width / 2 + 185 * self.hp_bar_size
        self.is_moving = True