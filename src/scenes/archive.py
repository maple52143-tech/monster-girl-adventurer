"""存档选择（对应旧项目 archieve_scene）：10 个存档位的轮盘。"""

from __future__ import annotations

import arcade

from src.core.app_state import app_state
from src.core.game_data import MODE_NAMES, character_display_name
from src.core.settings import ARCHIVE_SLOTS
from src.objects.ui import (Button, IconButton, Roulette, SlotCard, TextLabel,
                            draw_text, img_path)
from src.objects.ui_scene import UIScene


class Archive(UIScene):
    background = (28, 24, 32, 255)

    def __init__(self, window: arcade.Window):
        super().__init__(window)
        button_bg = img_path("images", "ui", "simple_button_bg.png")
        self.title = TextLabel((0.5, 0.90), "要窥探哪条时间线呢？", 40)
        self.left_btn = IconButton((0.075, 0.5), img_path("images", "ui", "button_l.png"),
                                   size=(130, 170), on_click=self._left)
        self.right_btn = IconButton((0.925, 0.5), img_path("images", "ui", "button_r.png"),
                                    size=(130, 170), on_click=self._right)
        self.back_btn = Button((0.10, 0.935), button_bg, "返回", size=(190, 94),
                               font_size=28, on_click=lambda: self.goto("menu"))
        self.roulette: Roulette | None = None
        self._build_roulette()
        # 顺序即层级：后加入的在上面。箭头要盖住轮盘卡片，否则点击会被卡片抢走
        self.add(self.roulette, self.left_btn, self.right_btn, self.back_btn, self.title)

    def on_show_view(self) -> None:
        super().on_show_view()
        self._refresh()

    # ------------------------------------------------------------ 构建

    def _card(self, slot: int) -> SlotCard:
        data = app_state.archives[slot]
        if data and data.get("character"):
            name = character_display_name(data["character"])
            mode = MODE_NAMES[int(data.get("mode", 0)) % len(MODE_NAMES)]
            subtitle = f"{name} · {mode}\n{data.get('updated_at', '')}"
        elif data:
            subtitle = "空白时间线\n（尚未开始）"
        else:
            subtitle = "无存档"
        # 旧排版：竖长条存档案卡（archive_button_bg 原图比例 861x1402）
        return SlotCard((0.5, 0.47), (300, 489), f"存档 {slot + 1}", subtitle,
                        on_click=lambda s=slot: self._choose(s), empty=not data,
                        bg=img_path("images", "ui", "archive_button_bg.png"),
                        title_color=(58, 44, 34, 255),
                        subtitle_color=(96, 78, 60, 255),
                        title_size=34, subtitle_size=22)

    def _build_roulette(self) -> None:
        cards = [self._card(i) for i in range(ARCHIVE_SLOTS)]
        # 旧排版：interval 290 / max_show 3（1200 宽屏），按 4:3 → 16:9 等比放大
        self.roulette = Roulette((0.5, 0.47), cards, spacing=380, max_show=3)
        self.roulette.pointer = min(app_state.current_archive or 0, ARCHIVE_SLOTS - 1)

    def _refresh(self) -> None:
        """重新读取存档数据并重建轮盘（进出场景时数据可能已变）。"""
        if self.roulette is not None and self.roulette in self.widgets:
            self.widgets.remove(self.roulette)
        app_state.reload()
        self._build_roulette()
        # 轮盘永远在最底层（放在列表最前）
        self.widgets.insert(0, self.roulette)

    # ------------------------------------------------------------ 绘制

    def draw_scene(self) -> None:
        draw_text("选择一条时间线，故事将由此展开。", self.window.width / 2, 96, 22,
                  (200, 190, 205, 200))

    def on_update(self, delta_time: float) -> None:
        super().on_update(delta_time)
        if self.roulette:
            self.left_btn.enabled = self.roulette.can_left
            self.right_btn.enabled = self.roulette.can_right
            self.left_btn.visible = self.roulette.can_left
            self.right_btn.visible = self.roulette.can_right

    # ------------------------------------------------------------ 交互

    def _left(self) -> None:
        if self.roulette:
            self.roulette.left()

    def _right(self) -> None:
        if self.roulette:
            self.roulette.right()

    def _choose(self, slot: int) -> None:
        new_start = app_state.enter_archive_from == "new_start"
        if new_start:
            msg = f"确定将「存档 {slot + 1}」作为开始新游戏的存档？"
        elif app_state.has_archive(slot):
            msg = f"读取「存档 {slot + 1}」继续游戏？"
        else:
            msg = f"「存档 {slot + 1}」还是空的，要在这里开始新游戏吗？"
        self.confirm(msg, lambda ok, s=slot: self._on_choose(ok, s))

    def _on_choose(self, ok: bool, slot: int) -> None:
        if not ok:
            return
        if app_state.enter_archive_from == "new_start":
            app_state.start_new_game(slot)
            self.goto("character")
            return
        if app_state.load_archive(slot) and app_state.current_character:
            self.goto("action")
        else:
            app_state.start_new_game(slot)
            self.goto("character")

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        super().on_key_press(symbol, modifiers)
        if symbol == arcade.key.ESCAPE:
            self.goto("menu")
