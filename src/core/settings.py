from pathlib import Path
"""
所有不可修改的游戏设置都在这里。
"""

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

HOME = Path(__file__).resolve().parent.parent.parent
ASSETS = HOME / "assets"
USERDATA = HOME / "userdata"

# --- UI / 场景（从 pygame 旧项目移植）---
FONT_FILE = ASSETS / "fonts" / "gfltt.ttf"
ARCHIVE_SLOTS = 10                 # 存档位数量
ARCHIVE_DIR = USERDATA / "archive"
SETTINGS_FILE = USERDATA / "settings.json"
UI_REPEAT_INTERVAL = 0.12          # 左右按钮长按连发的间隔
FADE_TIME = 0.35                   # 场景淡入淡出时长

# --- 战斗节奏（秒），调这三个值就能改手感 ---
TURN_END_DELAY = 0.35        # 玩家结束回合 -> 开始结算
ENEMY_ACTION_DELAY = 0.45    # 每个敌人出手之间的间隔
ENEMY_ANIM_TIME = 0.5        # 敌人出手立绘切换时长
ACTION_POINT_PER_TURN = 4
# 手牌上限：回合开始时“补到”这个张数，而不是无条件再加。
# 敌人塞进来的粘液牌会占用这个额度（塞满时抽不到新牌），但手牌不会无限膨胀。
HAND_SIZE = 4