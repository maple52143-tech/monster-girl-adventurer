import arcade
from arcade.future.light import Light, LightLayer

from src.core.resource_manager import res_manager
from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.game_window import GameWindow

class Loading(arcade.View):
    def __init__(self, window: GameWindow):
        super().__init__(window=window)
        self.sprites = arcade.SpriteList()
        self.title = arcade.Sprite(res_manager.image("sign"), scale=1.2, center_x=800, center_y=450)
        self.sprites.append(self.title)

        self.sound = res_manager.sound("music", "loading")

        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.light = Light(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 800, mode="soft")

        self.enter_time = 0
        self.lighted = False

    def on_show_view(self) -> None:
        self.window.background_color = arcade.csscolor.BLACK
        self.play_back = self.sound.play(0.5)

    def on_draw(self) -> bool | None:
        self.clear()
        with self.light_layer:
            self.sprites.draw()

        self.light_layer.draw(ambient_color=(0, 0, 0, 255))

    def on_update(self, delta_time: float) -> bool | None:
        self.enter_time += delta_time
        self.sprites.update()

        if self.enter_time >= 0.9 and not self.lighted:
            self.light_layer.add(self.light)
            self.lighted = True
        if self.enter_time >= 5.0:
            arcade.stop_sound(self.play_back)
            self.window.switch_scene("menu")




