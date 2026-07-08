import arcade

from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT

from src.objects.status_block import StatusBlock
from src.objects.character import Character


class Combat(arcade.View):

    def __init__(self, window: arcade.Window):
        super().__init__(window=window)
        self.sprites = arcade.SpriteList()

        self.character = Character("meowm")
        self.status_blocks = [StatusBlock(0, SCREEN_HEIGHT, self.character)]
        self.pointer = 0

    def on_show_view(self) -> None:
        self.background_color = arcade.csscolor.BLACK

    def on_update(self, delta_time: float) -> bool | None:
        for s in self.status_blocks:
            s.update()

    def on_draw(self) -> bool | None:
        self.clear()
        self.sprites.draw()
        for s in self.status_blocks:
            s.draw()