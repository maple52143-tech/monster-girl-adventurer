"""UI 场景基类：统一处理控件更新/绘制、消息框、提示框与淡入淡出切场景。

放在 objects/ 而不是 scenes/，是因为 GameWindow.auto_register 会把 scenes/ 里
所有 View 子类都实例化成场景——基类不该被注册。
"""

from __future__ import annotations

from typing import Callable

import arcade

from src.core.app_state import app_state
from src.core.settings import FADE_TIME, SCREEN_HEIGHT, SCREEN_WIDTH
from src.objects.ui import HintBox, MessageBox, Widget


class UIScene(arcade.View):
    background = (22, 19, 26, 255)
    music: str | None = None

    def __init__(self, window: arcade.Window):
        super().__init__(window=window)
        self.widgets: list[Widget] = []
        self.messagebox = MessageBox()
        self.hintbox = HintBox()
        self.background_color = self.background
        self._pending_scene: str | None = None
        self._switch_t = 0.0
        self._fade_in = 1.0
        # 本次按下命中的控件：抬起时只交给它，避免「箭头 + 下层卡片」同时触发
        self._pressed: Widget | None = None

    # ------------------------------------------------------------ 生命周期

    def on_show_view(self) -> None:
        self.background_color = self.background
        self._fade_in = 1.0
        from src.core.audio import audio
        if self.music:
            audio.play_music(self.music)

    def on_update(self, delta_time: float) -> None:
        self._fade_in = max(0.0, self._fade_in - delta_time / FADE_TIME)

        if self._pending_scene:
            self._switch_t += delta_time
            if self._switch_t >= FADE_TIME:
                target = self._pending_scene
                self._pending_scene = None
                self._switch_t = 0.0
                self.window.switch_scene(target)
                return

        for w in self.widgets:
            w.update(delta_time)
        self.messagebox.update(delta_time)
        self.hintbox.update(delta_time)

    def on_draw(self) -> None:
        self.clear()
        self.draw_scene()
        for w in self.widgets:
            w.draw()
        self.hintbox.draw()
        self.messagebox.draw()
        self._draw_transition()

    def _draw_transition(self) -> None:
        alpha = 0
        if self._fade_in > 0:
            alpha = int(self._fade_in * 255)
        elif self._pending_scene:
            alpha = int(min(1.0, self._switch_t / FADE_TIME) * 255)
        if alpha > 0:
            arcade.draw_rect_filled(
                arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT),
                (0, 0, 0, min(255, alpha)))

    # ------------------------------------------------------------ 子类钩子

    def draw_scene(self) -> None:
        """在控件之前绘制场景背景元素。"""

    # ------------------------------------------------------------ 工具

    def add(self, *widgets: Widget) -> None:
        for w in widgets:
            self.widgets.append(w)

    def goto(self, scene_name: str) -> None:
        """带淡出的场景切换。"""
        if self._pending_scene is None:
            self._pending_scene = scene_name
            self._switch_t = 0.0

    def confirm(self, message: str, callback: Callable[[bool], None]) -> None:
        self.messagebox.ask(message, callback)

    def show_hint(self, text: str) -> None:
        self.hintbox.show(text)

    # ------------------------------------------------------------ 输入

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        app_state.mouse_x, app_state.mouse_y = x, y
        if self.messagebox.visible:
            self.messagebox.on_mouse_motion(x, y)
            return
        for w in reversed(self.widgets):
            w.on_mouse_motion(x, y)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        app_state.mouse_x, app_state.mouse_y = x, y
        if self.messagebox.visible:
            self.messagebox.on_mouse_press(x, y, button)
            return
        # 只把点击交给最上层命中的控件，避免穿透到下层（例如存档翻页箭头压到卡片）
        for w in reversed(self.widgets):
            if w.hit_test(x, y):
                self._pressed = w
                w.on_mouse_press(x, y, button)
                break

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        app_state.mouse_x, app_state.mouse_y = x, y
        if self.messagebox.visible:
            self.messagebox.on_mouse_release(x, y, button)
            return
        target, self._pressed = self._pressed, None
        if target is not None:
            target.on_mouse_release(x, y, button)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> bool | None:
        if self.messagebox.visible:
            return
        for w in reversed(self.widgets):
            handler = getattr(w, "on_mouse_scroll", None)
            if handler and handler(x, y, scroll_y):
                return

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        if symbol == arcade.key.ESCAPE and self.messagebox.visible:
            self.messagebox.close(False)
