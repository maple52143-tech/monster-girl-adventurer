"""设置界面（对应旧项目 settings_scene）：音量、全屏、返回。"""

from __future__ import annotations

import arcade

from src.core.app_state import app_state
from src.core.audio import audio
from src.core.settings import SCREEN_HEIGHT, SCREEN_WIDTH
from src.objects.ui import Button, Picture, draw_text, img_path
from src.objects.ui_scene import UIScene


class Settings(UIScene):
    background = (20, 18, 24, 255)

    def __init__(self, window: arcade.Window):
        super().__init__(window)
        self.bg = Picture((0.5, 0.5), img_path("images", "ui", "settings_bg.png"),
                          size=(SCREEN_WIDTH, SCREEN_HEIGHT))
        button_bg = img_path("images", "ui", "simple_button_bg.png")
        self.minus_btn = Button((0.42, 0.56), button_bg, "-", size=(110, 92),
                                font_size=40, on_click=lambda: self._change_volume(-10))
        self.plus_btn = Button((0.58, 0.56), button_bg, "+", size=(110, 92),
                               font_size=36, on_click=lambda: self._change_volume(10))
        self.fullscreen_btn = Button((0.5, 0.40), button_bg, "", size=(300, 96),
                                     font_size=28, on_click=self._toggle_fullscreen)
        self.back_btn = Button((0.5, 0.22), button_bg, "返回主页", size=(260, 96),
                               font_size=28, on_click=lambda: self.goto("menu"))
        self.add(self.minus_btn, self.plus_btn, self.fullscreen_btn, self.back_btn)
        self._refresh_labels()

    # ------------------------------------------------------------ 逻辑

    def _refresh_labels(self) -> None:
        self.fullscreen_btn.label = "全屏：开" if app_state.settings.get("fullscreen") else "全屏：关"

    def _change_volume(self, delta: int) -> None:
        app_state.volume = app_state.volume + delta
        app_state.save_settings()
        audio.touch()

    def _toggle_fullscreen(self) -> None:
        value = not bool(app_state.settings.get("fullscreen"))
        app_state.settings["fullscreen"] = value
        app_state.save_settings()
        try:
            self.window.set_fullscreen(value)
        except Exception:      # noqa: BLE001 - 某些环境不支持切换全屏
            app_state.settings["fullscreen"] = False
        self._refresh_labels()

    # ------------------------------------------------------------ 绘制

    def on_show_view(self) -> None:
        super().on_show_view()
        self._refresh_labels()

    def draw_scene(self) -> None:
        self.bg.draw()
        arcade.draw_rect_filled(
            arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT),
            (0, 0, 0, 70))
        draw_text("设置", SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.86, 44, (255, 248, 236, 255))
        draw_text(f"音量：{app_state.volume}", SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.64,
                  30, (240, 235, 226, 255))
        draw_text("（音效与背景音乐共用此音量）", SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.48,
                  20, (200, 194, 204, 210))

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        super().on_key_press(symbol, modifiers)
        if symbol == arcade.key.ESCAPE:
            self.goto("menu")
