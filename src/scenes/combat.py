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

# 敌人全灭后等待多久再回到行动界面（秒）
BATTLE_END_DELAY = 1.2


class Combat(arcade.View):
    def __init__(self, window: arcade.Window):
        super().__init__(window=window)
        self.sprites = arcade.SpriteList()

        self.pointer = 0
        # 鼠标位置缓存：不依赖 window.mouse 的轮询状态（enable_polling=False / headless 时为 None）
        self.mouse_x = SCREEN_WIDTH / 2
        self.mouse_y = SCREEN_HEIGHT / 2

        self._battle_over_timer = 0.0
        self._returning = False
        self._start_battle()

        self.ap_show = arcade.Text("", 100, 100, (255, 255, 255, 255), 30)

        # 实验性添加着色器渲染
        self.shadertoy: Shadertoy = None
        self.channel0: Framebuffer = None
        self.channel1: Framebuffer = None
        self.load_shader()

    # ------------------------------------------------------------ 战斗装配

    def _start_battle(self):
        """构建（或重建）一场战斗。重建是为了战斗结束后能再进一次。"""
        self.character = EventedList([Character("meowm")])
        self.imagine_enemy = EventedList([Character("grassland_slime"), Character("grassland_slime")])

        status_manager.combat = [self.character, self.imagine_enemy]
        illu_manager.combat = [self.character, self.imagine_enemy]
        combat_manager.combat = [self.character, self.imagine_enemy]

        self.combat_show = CombatShow(self.character, self.imagine_enemy)
        self.deck = Deck(self.character[self.pointer], SCREEN_WIDTH / 2, 0)
        self.batch = pyglet.graphics.Batch()
        self.arrow = SelectArrow(self.deck, self.batch)

        self._battle_over_timer = 0.0
        self._returning = False

    def load_shader(self):
        window_size = self.window.size

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
        super().on_show_view()
        self.background_color = arcade.csscolor.BLACK
        # 上一场已经打完 / 尚未开战 → 重新装配一场
        if not combat_manager.is_combat or not combat_manager.enemy:
            self._start_battle()

    def on_update(self, delta_time: float) -> bool | None:
        self.combat_show.update(delta_time)
        self.deck.update(delta_time)
        illu_manager.update(delta_time)
        plot_manager.update(delta_time)
        status_manager.update_ptr()
        combat_manager.update(delta_time)
        self.arrow.update(self.mouse_x, self.mouse_y)
        self.ap_show.text = str(self.character[status_manager.team_ptr].action_point)

        # 敌人全灭 → 停留片刻后回到行动界面
        if combat_manager.is_combat and not combat_manager.enemy:
            self._battle_over_timer += delta_time
            if self._battle_over_timer >= BATTLE_END_DELAY and not self._returning:
                self._returning = True
                self.window.switch_scene("action")

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        self.mouse_x, self.mouse_y = x, y
        if not combat_manager.can_act:
            self.deck.touched = None
            return

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

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        self.mouse_x, self.mouse_y = x, y
        if not combat_manager.can_act:
            return                                   # 敌人回合中不接受出牌与选目标

        if button == arcade.MOUSE_BUTTON_LEFT and self.deck.selected is not None:
            self.deck.selected = self.deck.selected
        for card in self.deck.hand[::-1]:
            if card.collides_with_point((x, y)) and button == arcade.MOUSE_BUTTON_LEFT:
                self.deck.selected = card
                break

        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.deck.selected = None

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int) -> bool | None:
        self.on_mouse_motion(x, y, dx, dy)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.G:
            if combat_manager.request_end_turn():
                self.deck.selected = None

    def on_draw(self) -> bool | None:
        self.channel0.use()
        self.channel0.clear(color=arcade.color.BLACK)
        self.deck.draw_selected()

        if self.arrow.visible:
            self.batch.draw()
        self.sprites.draw()
        self.combat_show.draw()
        self.deck.draw()

        self.ap_show.draw()

        self.window.use()
        self.clear()
        self.shadertoy.render()
        self.deck.draw_selected()
        for s in plot_manager.show:
            s.draw()
