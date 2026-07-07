import arcade

from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.game_window import GameWindow

class Menu(arcade.View):
    def __init__(self, window: GameWindow):
        super().__init__(window=window)

        self.text = arcade.Text("Press any key to continue.", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                (255, 255, 255), 40, anchor_x="center", anchor_y="center")

    def on_show_view(self) -> None:
        self.background_color = arcade.csscolor.GRAY


    def on_draw(self) -> bool | None:
        self.clear()
        self.text.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        pass