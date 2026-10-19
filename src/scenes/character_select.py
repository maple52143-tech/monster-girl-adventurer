"""选择主角（对应旧项目 character_scene）。"""

from __future__ import annotations

import arcade

from src.core.app_state import app_state
from src.core.game_data import (avatar_path, character_data, character_display_name,
                                character_intro, list_characters)
from src.objects.ui import (Button, IconButton, Roulette, SlotCard, TextLabel,
                            img_path)
from src.objects.ui_scene import UIScene


class Character(UIScene):
    background = (30, 26, 34, 255)

    def __init__(self, window: arcade.Window):
        super().__init__(window)
        self.title = TextLabel((0.5, 0.89), "谁会是主角呢？", 40)
        self.left_btn = IconButton((0.1, 0.5), img_path("images", "ui", "button_l.png"),
                                   size=(130, 170), on_click=self._left)
        self.right_btn = IconButton((0.9, 0.5), img_path("images", "ui", "button_r.png"),
                                    size=(130, 170), on_click=self._right)
        self.back_btn = Button((0.10, 0.935), img_path("images", "ui", "simple_button_bg.png"),
                               "返回", size=(190, 94), font_size=28,
                               on_click=lambda: self.goto("archive"))
        self.roulette: Roulette | None = None
        self._build()
        # 箭头盖在轮盘卡片之上（后加入的在上层）
        self.add(self.roulette, self.left_btn, self.right_btn, self.back_btn, self.title)

    # ------------------------------------------------------------ 构建

    def _build(self) -> None:
        names = list_characters() or ["meowm"]
        cards = []
        for name in names:
            cards.append(SlotCard(
                (0.5, 0.5), (470, 640),
                character_display_name(name),
                character_intro(name) or "……",
                on_click=lambda n=name: self._choose(n),
                icon=avatar_path(name),
                title_size=36, subtitle_size=24,
            ))
        # 旧排版：一次只展示一张（max_show=1），左右按钮翻页
        self.roulette = Roulette((0.5, 0.48), cards, spacing=560, max_show=1)

    # ------------------------------------------------------------ 绘制 / 更新

    def on_update(self, delta_time: float) -> None:
        super().on_update(delta_time)
        if self.roulette:
            self.left_btn.visible = self.roulette.can_left
            self.right_btn.visible = self.roulette.can_right

    # ------------------------------------------------------------ 交互

    def _left(self) -> None:
        if self.roulette:
            self.roulette.left()

    def _right(self) -> None:
        if self.roulette:
            self.roulette.right()

    def _choose(self, name: str) -> None:
        self.confirm(f"确定选择「{character_display_name(name)}」作为主角吗？",
                     lambda ok, n=name: self._on_choose(ok, n))

    def _on_choose(self, ok: bool, name: str) -> None:
        if not ok:
            return
        data = character_data(name)
        app_state.set_character(name, list(data.get("initial_deck") or []))
        self.goto("prepare")

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        super().on_key_press(symbol, modifiers)
        if symbol == arcade.key.ESCAPE:
            self.goto("archive")
