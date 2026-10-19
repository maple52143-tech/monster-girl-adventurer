"""主页（对应旧项目 main_scene）：开始游戏 / 读取存档 / 回想 / 设置 / 退出。"""

from __future__ import annotations

import arcade

from src.core.app_state import app_state
from src.core.settings import SCREEN_HEIGHT, SCREEN_WIDTH
from src.objects.ui import Button, ZoomSlideshow, draw_text, img_path
from src.objects.ui_scene import UIScene

BG_NAMES = ["略", "妈妈", "满足", "喜欢", "生气", "哭哭"]

# 按钮尺寸按素材原始比例（1072x522 ≈ 2.05:1）换算，避免被拉伸
BUTTON_W, BUTTON_H = 230, 112


class Menu(UIScene):
    background = (18, 16, 22, 255)

    def __init__(self, window: arcade.Window):
        super().__init__(window)
        self.bg = ZoomSlideshow(img_path("images", "ui", "main_bg", f"{n}.png") for n in BG_NAMES)

        button_bg = img_path("images", "ui", "simple_button_bg.png")
        entries = [
            ("开始游戏", self._start_game),
            ("读取存档", self._load_game),
            ("回想", self._memory),
            ("设置", self._settings),
            ("退出", self._quit),
        ]
        # 旧排版：右侧竖排。间距略大于按钮高度，避免糊在一起
        spacing = 0.153
        self.buttons: list[Button] = []
        for i, (label, callback) in enumerate(entries):
            self.buttons.append(Button(
                (0.795, 0.72 - i * spacing), button_bg, label,
                size=(BUTTON_W, BUTTON_H), font_size=30,
                on_click=callback, label_offset=(0, 2)))
        self.add(*self.buttons)

    # ------------------------------------------------------------ 绘制

    def draw_scene(self) -> None:
        self.bg.draw()
        # 标题直接用游戏名（旧项目的「日行一善」标题图已弃用）
        draw_text("魔物娘也能当勇者？", SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.87,
                  52, (255, 250, 240, 255), shadow=True)
        draw_text("v0.1 · arcade 移植版", 90, 32, 20, (255, 255, 255, 150), shadow=True)

    def on_update(self, delta_time: float) -> None:
        super().on_update(delta_time)
        self.bg.update(delta_time, app_state.mouse_x, app_state.mouse_y)

    # ------------------------------------------------------------ 交互

    def _start_game(self) -> None:
        app_state.enter_archive_from = "new_start"
        self.goto("archive")

    def _load_game(self) -> None:
        app_state.enter_archive_from = "archive"
        self.goto("archive")

    def _memory(self) -> None:
        self.confirm("回想功能尚未开放，敬请期待。", lambda ok: None)

    def _settings(self) -> None:
        self.goto("settings")

    def _quit(self) -> None:
        self.confirm("确定要退出游戏吗？", self._confirm_quit)

    @staticmethod
    def _confirm_quit(ok: bool) -> None:
        if ok:
            arcade.exit()
