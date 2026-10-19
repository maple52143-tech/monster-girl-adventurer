"""行动主界面（对应旧项目 action_scene）：状态图标 + 事件轮盘。"""

from __future__ import annotations

import arcade

from src.core.app_state import app_state
from src.core.game_data import (MODE_NAMES, character_data, character_display_name,
                                illustration_path)
from src.objects.ui import (Button, IconButton, Roulette, SlotCard, TextLabel,
                            draw_text, fit_picture, img_path, texture)
from src.objects.ui_scene import UIScene

EVENTS = ["combat", "rest", "adventure", "trade", "choice"]
EVENT_NAMES = {
    "combat": "战斗", "rest": "休息", "adventure": "冒险",
    "trade": "交易", "choice": "抉择",
}
EVENT_HINTS = {
    "combat": "遭遇敌人，进入战斗。",
    "rest": "原地休息，恢复一些体力并度过一天。",
    "adventure": "探索未知区域（尚未开放）。",
    "trade": "与商人交换物资（尚未开放）。",
    "choice": "面对一次抉择（尚未开放）。",
}


class Action(UIScene):
    background = (22, 20, 28, 255)

    def __init__(self, window: arcade.Window):
        super().__init__(window)
        button_bg = img_path("images", "ui", "simple_button_bg.png")
        self.illustration = None
        self.name_label = TextLabel((0.225, 0.10), "", 36)
        self.info_label = TextLabel((0.5, 0.885), "", 24)

        # 顶部状态图标（装饰 + 数值）
        self.status_icons = {
            "health": IconButton((0.395, 0.945), img_path("images", "ui", "icons", "health.png"),
                                 scale=0.085, on_click=lambda: self._info("health")),
            "magic": IconButton((0.535, 0.945), img_path("images", "ui", "icons", "magic.png"),
                                scale=0.085, on_click=lambda: self._info("magic")),
            "coins": IconButton((0.675, 0.945), img_path("images", "ui", "icons", "coins.png"),
                                scale=0.085, on_click=lambda: self._info("coins")),
            "card_num": IconButton((0.79, 0.945), img_path("images", "ui", "icons", "card_num.png"),
                                   scale=0.085, on_click=lambda: self._info("card_num")),
        }

        # 底部事件图标
        self.event_icons: list[IconButton] = []
        for i, key in enumerate(EVENTS):
            self.event_icons.append(IconButton(
                (0.365 + i * 0.088, 0.10),
                img_path("images", "ui", "icons", f"{key}.png"),
                scale=0.075, on_click=lambda k=key: self._info(k)))
        self.ap_icon = IconButton((0.365 + 5 * 0.088, 0.10),
                                  img_path("images", "ui", "icons", "action_point.png"),
                                  scale=0.075, on_click=lambda: self._info("action_point"))

        # 事件轮盘
        cards = [
            SlotCard((0.70, 0.52), (340, 430), "战斗", "遭遇敌人，进入战斗",
                     on_click=self._battle, icon=img_path("images", "ui", "icons", "combat.png")),
            SlotCard((0.70, 0.52), (340, 430), "休息", "恢复体力，度过一天",
                     on_click=self._rest, icon=img_path("images", "ui", "icons", "rest.png")),
            SlotCard((0.70, 0.52), (340, 430), "冒险", "探索未知区域",
                     on_click=self._adventure, icon=img_path("images", "ui", "icons", "adventure.png")),
        ]
        self.roulette = Roulette((0.70, 0.52), cards, spacing=380, max_show=3)

        self.save_btn = Button((0.94, 0.935), button_bg, "保存", size=(150, 78),
                               font_size=27, on_click=self._save)
        self.back_btn = Button((0.10, 0.935), button_bg, "返回主页", size=(200, 74),
                               font_size=26, on_click=lambda: self.goto("menu"))

        self.add(self.name_label, self.info_label, *self.status_icons.values(),
                 *self.event_icons, self.ap_icon, self.save_btn, self.back_btn,
                 self.roulette)

    # ------------------------------------------------------------ 进入场景

    def on_show_view(self) -> None:
        super().on_show_view()
        name = app_state.current_character or "meowm"
        data = character_data(name)
        status = data.get("initial_status") or {}
        self._hp = status.get("max_hp", 0)
        self._mp = status.get("max_mp", 0)
        self._cards = len(app_state.current_deck) or len(data.get("initial_deck") or [])
        self._coins = app_state.coins

        self.name_label.text = character_display_name(name)
        if self.illustration is not None and self.illustration in self.widgets:
            self.widgets.remove(self.illustration)
        path = illustration_path(name)
        if path:
            self.illustration = fit_picture((0.225, 0.55), path, (560, 660))
            self.widgets.insert(0, self.illustration)

        self._refresh_info()
        self.hintbox.hide()

    def _refresh_info(self) -> None:
        mode = MODE_NAMES[app_state.game_mode % len(MODE_NAMES)]
        self.info_label.text = f"第 {app_state.day} 天 · {mode}"

    # ------------------------------------------------------------ 绘制

    def draw_scene(self) -> None:
        y = 0.945 * 900
        for key, value in (("health", f"{self._hp:g}"), ("magic", f"{self._mp:g}"),
                           ("coins", str(self._coins)), ("card_num", str(self._cards))):
            icon = self.status_icons[key]
            draw_text(value, icon.x + 34, y, 26, (240, 235, 226, 255), anchor_x="left")
        draw_text(str(app_state.action_point), self.ap_icon.x + 32, self.ap_icon.y, 24,
                  (240, 235, 226, 255), anchor_x="left")

    def on_update(self, delta_time: float) -> None:
        super().on_update(delta_time)
        hovered = next((b for b in self.event_icons if b.hovered), None)
        if hovered is not None:
            idx = self.event_icons.index(hovered)
            self.show_hint(EVENT_HINTS.get(EVENTS[idx], ""))
        else:
            self.hintbox.hide()

    # ------------------------------------------------------------ 交互

    def _info(self, key: str) -> None:
        text = {
            "health": f"当前生命：{self._hp:g}",
            "magic": f"当前魔力：{self._mp:g}",
            "coins": f"持有金币：{self._coins}",
            "card_num": f"牌组张数：{self._cards}",
            "action_point": f"行动点：{app_state.action_point}",
        }.get(key, EVENT_HINTS.get(key, ""))
        if text:
            self.show_hint(text)

    def _battle(self) -> None:
        self.confirm("前方出现了敌人，要迎战吗？", self._on_battle)

    def _on_battle(self, ok: bool) -> None:
        if ok:
            self.goto("combat")

    def _rest(self) -> None:
        self.confirm("在此休息，度过一天？", self._on_rest)

    def _on_rest(self, ok: bool) -> None:
        if not ok:
            return
        app_state.day += 1
        self._refresh_info()
        if app_state.current_archive is not None:
            app_state.save_archive(app_state.current_archive)
        self.confirm("你安稳地睡了一觉，体力恢复了一些。", lambda _ok: None)

    def _adventure(self) -> None:
        self.confirm("前方一片迷雾，冒险内容尚未开放。", lambda ok: None)

    def _save(self) -> None:
        if app_state.current_archive is None:
            self.confirm("当前没有绑定存档位，请从主页重新开始。", lambda ok: None)
            return
        app_state.save_archive(app_state.current_archive)
        self.confirm(f"已保存到「存档 {app_state.current_archive + 1}」。", lambda ok: None)

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        super().on_key_press(symbol, modifiers)
        if symbol == arcade.key.ESCAPE:
            self.goto("menu")

