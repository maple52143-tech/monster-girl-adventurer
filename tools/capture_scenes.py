"""把各场景截图保存到 draft/ 以便人工检查布局。"""

import os
import sys
from pathlib import Path

ROOT = Path(r"D:\Develop\PythonProject\monster-girl-adventurer")
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import arcade
import arcade.resources

arcade.resources.add_resource_handle("assets", str(ROOT / "assets"))

import src.core.settings as settings
from src.core.app_state import app_state
from src.core.game_window import GameWindow

out_dir = ROOT / "draft" / "scenes"
out_dir.mkdir(parents=True, exist_ok=True)

window = GameWindow(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, "shots")
window.auto_register(ROOT / "src" / "scenes")

# 先跑一遍流程，让全局状态有意义
app_state.start_new_game(0)
app_state.set_character("meowm", ["attack", "attack", "defense"])
app_state.game_mode = 0
app_state.current_archive = 0
app_state.day = 3
app_state.coins = 25
app_state.action_point = 4

names = ["menu", "archive", "character", "prepare", "action", "settings"]
for name in names:
    window.switch_scene(name)
    view = window.scenes[name]
    window.dispatch_events()
    view.on_show_view()
    for _ in range(40):
        view.on_update(1 / 60)
        view.on_mouse_motion(1200, 450, 0, 0)
    # 直接渲染到离屏 framebuffer：这台机器上 arcade.get_image() 读不到内容
    fb = window.ctx.framebuffer(
        color_attachments=[window.ctx.texture((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))])
    with fb:
        fb.clear(color=(0, 0, 0, 255))
        view.on_draw()
    data = fb.read(viewport=(0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), components=4)
    import numpy as np
    from PIL import Image
    arr = np.frombuffer(data, dtype=np.uint8).reshape(
        settings.SCREEN_HEIGHT, settings.SCREEN_WIDTH, 4)
    path = out_dir / f"{name}.png"
    Image.fromarray(arr).transpose(Image.FLIP_TOP_BOTTOM).convert("RGB").save(path)
    print("saved", path)

# 额外截一张确认框
window.switch_scene("menu")
menu = window.scenes["menu"]
menu.on_show_view()
menu.confirm("确定要退出游戏吗？", lambda ok: None)
for _ in range(40):
    menu.on_update(1 / 60)
fb = window.ctx.framebuffer(
    color_attachments=[window.ctx.texture((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))])
with fb:
    menu.on_draw()
data = fb.read(viewport=(0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), components=4)
import numpy as np
from PIL import Image
arr = np.frombuffer(data, dtype=np.uint8).reshape(
    settings.SCREEN_HEIGHT, settings.SCREEN_WIDTH, 4)
Image.fromarray(arr).transpose(Image.FLIP_TOP_BOTTOM).convert("RGB").save(out_dir / "menu_confirm.png")
print("saved menu_confirm")

app_state.delete_archive(0)



