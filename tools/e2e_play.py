"""端到端模拟：用真实窗口事件（dispatch_event）走完整流程并截图。

与 capture_scenes.py 的区别：这里不直接调用控件方法，而是像玩家一样
派发 on_mouse_press / on_mouse_release / on_mouse_motion，验证事件路由本身。
"""

import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(r"D:\Develop\PythonProject\monster-girl-adventurer")
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import arcade
import arcade.resources

arcade.resources.add_resource_handle("assets", str(ROOT / "assets"))

import src.core.settings as settings
from src.core.app_state import app_state
from src.core.combat_manager import combat_manager
from src.core.game_window import GameWindow

OUT = ROOT / "draft" / "e2e"
OUT.mkdir(parents=True, exist_ok=True)

window = GameWindow(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, "e2e")
window.auto_register(ROOT / "src" / "scenes")

log = []


def view():
    return window.current_view


def pump(seconds: float = 0.4):
    """让当前场景推进若干帧，直到场景切换/淡入完成。"""
    frames = max(1, int(seconds * 60))
    for _ in range(frames):
        v = view()
        if v is None:
            return
        v.on_update(1 / 60)
        v.on_draw()
    window.flip()


def mouse(x, y):
    v = view()
    if v is not None:
        v.on_mouse_motion(int(x), int(y), 0, 0)


def click(x, y):
    v = view()
    if v is None:
        return
    v.on_mouse_motion(int(x), int(y), 0, 0)
    v.on_mouse_press(int(x), int(y), 1, 0)
    v.on_mouse_release(int(x), int(y), 1, 0)


def shot(name: str):
    v = view()
    fb = window.ctx.framebuffer(
        color_attachments=[window.ctx.texture((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))])
    with fb:
        fb.clear(color=(0, 0, 0, 255))
        v.on_draw()
    data = fb.read(viewport=(0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), components=4)
    arr = np.frombuffer(data, dtype=np.uint8).reshape(
        settings.SCREEN_HEIGHT, settings.SCREEN_WIDTH, 4)
    path = OUT / f"{name}.png"
    Image.fromarray(arr).transpose(Image.FLIP_TOP_BOTTOM).convert("RGB").save(path)
    log.append(f"saved {name}: view={type(v).__name__}")


def scene_name():
    return window.current_scene_name


def assert_scene(expected: str):
    actual = scene_name()
    log.append(f"  scene={actual} (expect {expected}) {'OK' if actual == expected else 'MISMATCH'}")
    return actual == expected


# ---------------------------------------------------------------- 流程
window.switch_scene("menu")
pump(1.0)
shot("01_menu")
assert_scene("menu")

menu = view()
click(menu.buttons[0].x, menu.buttons[0].y)          # 开始游戏
pump(0.8)
shot("02_archive")
assert_scene("archive")

arch = view()
# 先点右箭头：不应触发下面的卡片
click(arch.right_btn.x, arch.right_btn.y)
pump(0.5)
log.append(f"  arrow -> pointer={arch.roulette.pointer} dialog={arch.messagebox.visible}")
shot("03_archive_after_arrow")

# 点当前卡片 -> 确认
card = arch.roulette.items[arch.roulette.pointer]
click(card.x, card.y)
pump(0.2)
log.append(f"  card click -> dialog={arch.messagebox.visible}")
shot("04_archive_confirm")
click(settings.SCREEN_WIDTH * 0.445, settings.SCREEN_HEIGHT * 0.40)   # 确定
pump(0.8)
assert_scene("character")

ch = view()
click(ch.roulette.items[ch.roulette.pointer].x, ch.roulette.items[ch.roulette.pointer].y)
pump(0.2)
shot("05_character_confirm")
click(settings.SCREEN_WIDTH * 0.445, settings.SCREEN_HEIGHT * 0.40)
pump(0.8)
assert_scene("prepare")
shot("06_prepare")

prep = view()
click(prep.mode_buttons[0].x, prep.mode_buttons[0].y)
pump(0.2)
shot("07_prepare_confirm")
click(settings.SCREEN_WIDTH * 0.445, settings.SCREEN_HEIGHT * 0.40)
pump(0.9)
assert_scene("action")
shot("08_action")

act = view()
click(act.roulette.items[0].x, act.roulette.items[0].y)
pump(0.2)
shot("09_action_confirm")
click(settings.SCREEN_WIDTH * 0.445, settings.SCREEN_HEIGHT * 0.40)
pump(1.0)
assert_scene("combat")
pump(0.6)
shot("10_combat")

# 直接把敌人打死，验证自动回流
for foe in list(combat_manager.enemy):
    foe.hp = 0
pump(2.5)
assert_scene("action")
shot("11_back_to_action")

print("\n".join(log))
