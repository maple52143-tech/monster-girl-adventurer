import arcade

from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.status_manager import status_manager

from src.objects.status_block import StatusBlock
from src.objects.character import Character
from src.objects.deck import Deck


class Combat(arcade.View):

    def __init__(self, window: arcade.Window):
        super().__init__(window=window)
        self.sprites = arcade.SpriteList()

        self.pointer = 0
        self.character = [Character("meowm")]
        self.imagine_enemy = [Character("grassland_slime")]
        self.status_blocks = [StatusBlock(0, SCREEN_HEIGHT, self.character[0])]
        self.deck = Deck(self.character[self.pointer], SCREEN_WIDTH / 2, 0)

        status_manager.combat = [self.character, self.imagine_enemy]

    def on_show_view(self) -> None:
        self.background_color = arcade.csscolor.BLACK

    def on_update(self, delta_time: float) -> bool | None:
        for s in self.status_blocks:
            s.update()
        self.deck.update()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        for card in self.deck.hand[::-1]:
            if card.collides_with_point((x, y)):
                self.deck.sprites.remove(card)
                self.deck.sprites.append(card)
                return

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        for card in self.deck.hand[::-1]:
            if card.collides_with_point((x, y)):
                card.use_card()
                self.deck.hand.remove(card)

                self.deck.update_card()
                return

    def on_draw(self) -> bool | None:
        self.clear()
        self.sprites.draw()
        for s in self.status_blocks:
            s.draw()
        self.deck.draw()
        arcade.draw_text(f"health: {self.imagine_enemy[0].hp}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, font_size=20)