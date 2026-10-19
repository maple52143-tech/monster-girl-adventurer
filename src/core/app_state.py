"""全局运行状态（对应旧 pygame 项目的 shared_data.shared）。

负责：当前存档/角色/模式等局内数据、10 个存档位的读写、用户设置持久化。
只读写 ``userdata/`` 目录，不碰 assets 与旧项目。
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from src.core.settings import ARCHIVE_DIR, ARCHIVE_SLOTS, SETTINGS_FILE, USERDATA


def _read_json(path: Path, default: Any) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except (json.JSONDecodeError, OSError):
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


DEFAULT_SETTINGS = {
    "volume": 100,        # 0~100
    "fullscreen": False,
    "last_character": "meowm",
}


class AppState:
    """单例式全局状态。旧项目里叫 ``shared``。"""

    def __init__(self):
        # 鼠标（视图坐标）
        self.mouse_x = 0
        self.mouse_y = 0
        # 存档与流程
        self.current_archive: int | None = None
        self.enter_archive_from = "new_start"     # new_start / archive
        self.current_character: str | None = None
        self.current_deck: list[str] = []
        self.current_team: list[str] = []
        self.game_mode = 0                        # 0 普通 / 1 困难 / 2 轮战 / 3 自定义
        self.day = 1
        self.coins = 0
        self.action_point = 0
        # 设置
        self.stats: dict[str, Any] = {}
        self.settings = dict(DEFAULT_SETTINGS)
        self.archives: list[dict | None] = [None] * ARCHIVE_SLOTS
        self.reload()

    # ------------------------------------------------------------ 持久化

    def reload(self) -> None:
        USERDATA.mkdir(parents=True, exist_ok=True)
        self.settings = {**DEFAULT_SETTINGS, **_read_json(SETTINGS_FILE, {})}
        self.archives = [self._read_archive(i) for i in range(ARCHIVE_SLOTS)]

    def _archive_path(self, slot: int) -> Path:
        return ARCHIVE_DIR / f"data_{slot}.json"

    def _read_archive(self, slot: int) -> dict | None:
        data = _read_json(self._archive_path(slot), None)
        if not data:
            return None
        return data

    def save_settings(self) -> None:
        _write_json(SETTINGS_FILE, self.settings)

    # ------------------------------------------------------------ 存档

    @property
    def volume(self) -> int:
        return int(self.settings.get("volume", 100))

    @volume.setter
    def volume(self, value: int) -> None:
        self.settings["volume"] = max(0, min(100, int(value)))

    def has_archive(self, slot: int) -> bool:
        return 0 <= slot < ARCHIVE_SLOTS and self.archives[slot] is not None

    def save_archive(self, slot: int) -> dict | None:
        """把当前局内进度写入指定存档位，返回存档内容。"""
        if not (0 <= slot < ARCHIVE_SLOTS):
            return None
        payload = {
            "character": self.current_character,
            "deck": list(self.current_deck),
            "team": list(self.current_team),
            "mode": self.game_mode,
            "day": self.day,
            "coins": self.coins,
            "updated_at": time.strftime("%Y-%m-%d %H:%M"),
        }
        self.archives[slot] = payload
        _write_json(self._archive_path(slot), payload)
        return payload

    def load_archive(self, slot: int) -> bool:
        """读取存档并写入当前状态。"""
        if not self.has_archive(slot):
            return False
        data = self.archives[slot] or {}
        self.current_archive = slot
        self.current_character = data.get("character")
        self.current_deck = list(data.get("deck") or [])
        self.current_team = list(data.get("team") or [])
        self.game_mode = int(data.get("mode", 0))
        self.day = int(data.get("day", 1))
        self.coins = int(data.get("coins", 0))
        return True

    def delete_archive(self, slot: int) -> None:
        if 0 <= slot < ARCHIVE_SLOTS:
            self.archives[slot] = None
            self._archive_path(slot).unlink(missing_ok=True)

    # ------------------------------------------------------------ 开新局

    def start_new_game(self, slot: int | None = None) -> None:
        """从「开始游戏」进入：清空局内状态，必要时占一个存档位。"""
        self.current_archive = slot
        self.current_character = None
        self.current_deck = []
        self.current_team = []
        self.game_mode = 0
        self.day = 1
        self.coins = 0
        self.action_point = 0
        if slot is not None:
            self.archives[slot] = {}

    def set_character(self, name: str, initial_deck: list[str]) -> None:
        self.current_character = name
        self.current_deck = list(initial_deck)
        if name not in self.current_team:
            self.current_team.append(name)
        self.settings["last_character"] = name


app_state = AppState()
