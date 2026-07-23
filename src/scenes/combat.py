import arcade

from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.status_manager import status_manager
from src.core.illustration_manager import illu_manager
from src.core.plot_manager import plot_manager
from src.core.combat_manager import combat_manager

from src.objects.status_block import StatusBlock
from src.objects.character import Character
from src.objects.character_block import CharacterBlock
from src.objects.deck import Deck


class Combat(arcade.View):

    def __init__(self, window: arcade.Window):
        super().__init__(window=window)
        self.sprites = arcade.SpriteList()

        self.pointer = 0
        self.character = [Character("meowm")]
        self.imagine_enemy = [Character("grassland_slime")]

        status_manager.combat = [self.character, self.imagine_enemy]
        illu_manager.combat = [self.character, self.imagine_enemy]
        combat_manager.combat = [self.character, self.imagine_enemy]

        self.status_blocks = [StatusBlock(0, SCREEN_HEIGHT, self.character[0])]
        self.character_blocks = [CharacterBlock(SCREEN_WIDTH * 0.3, SCREEN_HEIGHT / 2, self.character[0]),
                                 CharacterBlock(SCREEN_WIDTH * 0.7, SCREEN_HEIGHT / 2, self.imagine_enemy[0])]
        self.deck = Deck(self.character[self.pointer], SCREEN_WIDTH / 2, 0)

    def on_show_view(self) -> None:
        self.background_color = arcade.csscolor.BLACK

    def on_update(self, delta_time: float) -> bool | None:
        for s in self.status_blocks:
            s.update()
        for c in self.character_blocks:
            c.update()
        self.deck.update(delta_time)
        illu_manager.update(delta_time)
        plot_manager.update(delta_time)
        combat_manager.update()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        card_touched = False
        for card in self.deck.hand[::-1]:
            if card.collides_with_point((x, y)):
                self.deck.touched = card
                card_touched = True
                break
        if not card_touched:
            self.deck.touched = None

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        for card in self.deck.hand[::-1]:
            if card.collides_with_point((x, y)) and button == arcade.MOUSE_BUTTON_LEFT:
                self.deck.selected = card
                break

        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.deck.selected = None

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.G:
            combat_manager.new_round()

    def on_draw(self) -> bool | None:
        self.clear()
        self.sprites.draw()
        for s in self.status_blocks:
            s.draw()
        for c in self.character_blocks:
            c.draw()
        self.deck.draw()
        arcade.draw_text(f"health: {self.imagine_enemy[0].hp}", SCREEN_WIDTH / 10 * 7, SCREEN_HEIGHT / 2, font_size=20)
        for s in plot_manager.show:
            s.draw()