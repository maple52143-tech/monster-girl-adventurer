from psygnal.containers import EventedList
import arcade
from arcade.experimental import Shadertoy
from arcade.gl.framebuffer import Framebuffer
import pyglet

from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.status_manager import status_manager
from src.core.illustration_manager import illu_manager
from src.core.plot_manager import plot_manager
from src.core.combat_manager import combat_manager
from src.core.resource_manager import res_manager

from src.objects.character import Character
from src.objects.combat_show import CombatShow
from src.objects.deck import Deck
from src.objects.select_arrow import SelectArrow


class Combat(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__(window=window)
        self.sprites = arcade.SpriteList()

        self.pointer = 0
        self.character = EventedList([Character("meowm")])
        self.imagine_enemy = EventedList([Character("grassland_slime"), Character("grassland_slime")])

        status_manager.combat = [self.character, self.imagine_enemy]
        illu_manager.combat = [self.character, self.imagine_enemy]
        combat_manager.combat = [self.character, self.imagine_enemy]


        self.combat_show = CombatShow(self.character, self.imagine_enemy)
        self.deck = Deck(self.character[self.pointer], SCREEN_WIDTH / 2, 0)
        self.batch = pyglet.graphics.Batch()
        self.arrow = SelectArrow(self.deck, self.batch)

        # 实验性添加着色器渲染
        self.shadertoy: Shadertoy = None
        self.channel0: Framebuffer = None
        self.channel1: Framebuffer = None
        self.load_shader()

    def load_shader(self):
        window_size = self.window.size
        print(window_size)

        self.shadertoy = Shadertoy(window_size, res_manager.shader("selected_card"))

        self.channel0 = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture(window_size, components=4)]
        )
        self.channel1 = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture(window_size, components=4)]
        )

        self.shadertoy.channel_0 = self.channel0.color_attachments[0]
        self.shadertoy.channel_1 = self.channel1.color_attachments[0]

    def on_show_view(self) -> None:
        self.background_color = arcade.csscolor.BLACK

    def on_update(self, delta_time: float) -> bool | None:
        self.combat_show.update()
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

        if self.deck.selected is not None:
            self.combat_show.select(x)

        self.arrow.update(x, y)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        if button == arcade.MOUSE_BUTTON_LEFT and self.deck.selected is not None:
            self.deck.selected = self.deck.selected
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
        self.channel0.use()
        self.channel0.clear(color=arcade.color.BLACK)
        self.deck.draw_selected()

        # self.channel1.use()
        # self.channel1.clear(color=arcade.color.BLACK)
        if self.arrow.visible:
            self.batch.draw()
        self.sprites.draw()
        self.combat_show.draw()
        self.deck.draw()

        self.window.use()
        self.clear()
        self.shadertoy.render()
        self.deck.draw_selected()
        # arcade.draw_text(f"health: {self.imagine_enemy[0].hp}", SCREEN_WIDTH / 10 * 7, SCREEN_HEIGHT / 2, font_size=20)
        for s in plot_manager.show:
            s.draw()