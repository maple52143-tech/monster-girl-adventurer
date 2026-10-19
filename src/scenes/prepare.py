"""出战准备（对应旧项目 prepare_scene）：展示立绘、选择模式。"""

from __future__ import annotations

import arcade

from src.core.app_state import app_state
from src.core.game_data import (MODE_HINTS, MODE_NAMES, character_data,
                                character_display_name, illustration_path)
from src.objects.ui import (Button, TextLabel, draw_text, fit_picture, img_path)
from src.objects.ui_scene import UIScene


class Prepare(UIScene):
    background = (24, 22, 30, 255)

    def __init__(self, window: arcade.Window):
        super().__init__(window)
        button_bg = img_path("images", "ui", "simple_button_bg.png")
        self.illustration = None
        self.name_label = TextLabel((0.20, 0.115), "", 38)
        self.mode_title = TextLabel((0.67, 0.815), "选择模式！", 34)
        # 旧排版：四种模式横排一行（按钮按素材比例 2.05:1，不做拉伸）
        self.mode_buttons: list[Button] = []
        for i, mode in enumerate(MODE_NAMES):
            self.mode_buttons.append(Button(
                (0.45 + i * 0.147, 0.70), button_bg, mode, size=(246, 120),
                font_size=28, on_click=lambda idx=i: self._choose_mode(idx)))
        self.enhance_btn = Button((0.51, 0.163), button_bg, "潜能强化", size=(200, 98),
                                  font_size=25, on_click=self._enhance)
        self.preview_btn = Button((0.825, 0.163), button_bg, "卡牌预览", size=(200, 98),
                                  font_size=25, on_click=self._preview)
        self.back_btn = Button((0.10, 0.935), button_bg, "返回", size=(170, 74),
                               font_size=28, on_click=lambda: self.goto("character"))
        self.add(self.name_label, self.mode_title, *self.mode_buttons,
                 self.enhance_btn, self.preview_btn, self.back_btn)

    # ------------------------------------------------------------ 进入场景

    def on_show_view(self) -> None:
        super().on_show_view()
        name = app_state.current_character or "meowm"
        self.name_label.text = character_display_name(name)
        data = character_data(name)

        if self.illustration is not None and self.illustration in self.widgets:
            self.widgets.remove(self.illustration)
        path = illustration_path(name)
        if path:
            self.illustration = fit_picture((0.20, 0.55), path, (520, 640))
            self.widgets.insert(0, self.illustration)

        hp = (data.get("initial_status") or {}).get("max_hp", 0)
        mp = (data.get("initial_status") or {}).get("max_mp", 0)
        self._stats_text = f"生命 {hp:g}    魔力 {mp:g}    牌组 {len(data.get('initial_deck') or [])} 张"
        self.hintbox.hide()

    # ------------------------------------------------------------ 绘制

    def draw_scene(self) -> None:
        draw_text(getattr(self, "_stats_text", ""), 0.20 * self.window.width, 0.075 * 900,
                  24, (214, 206, 222, 235))

    def on_update(self, delta_time: float) -> None:
        super().on_update(delta_time)
        hovered = next((b for b in self.mode_buttons if b.hovered), None)
        if hovered is not None:
            self.show_hint(MODE_HINTS.get(hovered.label, ""))
        else:
            self.hintbox.hide()

    # ------------------------------------------------------------ 交互

    def _choose_mode(self, index: int) -> None:
        mode = MODE_NAMES[index]
        self.confirm(f"确定要以「{mode}」进行游戏吗？",
                     lambda ok, i=index: self._on_mode(ok, i))

    def _on_mode(self, ok: bool, index: int) -> None:
        if not ok:
            return
        app_state.game_mode = index
        if app_state.current_archive is not None:
            app_state.save_archive(app_state.current_archive)
        self.goto("action")

    def _enhance(self) -> None:
        self.confirm("潜能强化尚未开放。", lambda ok: None)

    def _preview(self) -> None:
        self.confirm("卡牌预览尚未开放。", lambda ok: None)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        super().on_key_press(symbol, modifiers)
        if symbol == arcade.key.ESCAPE:
            self.goto("character")
