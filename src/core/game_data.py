"""角色 / 模式等静态数据读取（对应旧项目 shared.character 与 character_scene 的列表）。"""

from __future__ import annotations

import json
from pathlib import Path

from src.core.settings import ASSETS

MODE_NAMES = ["普通模式", "困难模式", "轮战模式", "自定义模式"]
MODE_HINTS = {
    "普通模式": "普通模式。这里的敌人能力不算太强，不会对魔物娘造成很大的威胁。如果初次游玩推荐选择此模式。",
    "困难模式": "困难模式。敌人的攻击意图更加显著，各项能力也有所提升。",
    "轮战模式": "轮战模式。连续与多组敌人交战，中途不回复。",
    "自定义模式": "自定义模式。自行组合遭遇与难度（尚未开放）。",
}

CHARACTER_DIR = ASSETS / "data" / "character"
AVATAR_DIR = ASSETS / "images" / "avatar"
ILLUSTRATION_DIR = ASSETS / "images" / "illustration"


def list_characters() -> list[str]:
    """可选角色（data/character 下的文件名，按名称排序）。"""
    if not CHARACTER_DIR.exists():
        return []
    return sorted(p.stem for p in CHARACTER_DIR.glob("*.json"))


def character_data(name: str) -> dict:
    path = CHARACTER_DIR / f"{name}.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def character_display_name(name: str) -> str:
    return character_data(name).get("name") or name


def character_intro(name: str) -> str:
    return character_data(name).get("introduction") or ""


def avatar_path(name: str) -> str | None:
    p = AVATAR_DIR / f"avatar_{name}.png"
    return str(p) if p.exists() else None


def illustration_path(name: str) -> str | None:
    p = ILLUSTRATION_DIR / f"illustration_{name}.png"
    return str(p) if p.exists() else None
