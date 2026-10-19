"""第 1~2 批修改的回归自测。

运行：  .venv\\Scripts\\python.exe tools\\verify_changes.py

会创建一个隐藏的 1600x900 窗口（需要能创建 OpenGL 上下文的桌面环境；
这也意味着它会短暂占用一个窗口句柄，但不会显示在屏幕上）。

覆盖：
  A2  hp 归零即死亡
  A4  战斗块淡出后保留槽位（不再从列表删除）+ 指针指向存活单位
  A6  效果类显式解析（EFFECT_CLASS）
  B1  行动点不足时 use_card() 返回 False
  B3  遍历中删除的安全写法
  B4  is_hurt 置位规则（护盾挡下不算）与回合开始复位
  B5  卡牌效果第三段参数
  C1  StandardSet.parts 不再随重建累积
  C3  plot_manager follow 独占
  末尾额外跑一次 Combat.on_draw()，覆盖绘制路径（含 Shadertoy、Deck、StatusBlock）
"""

import os
import sys
from pathlib import Path

# 注意：不要强制 ARCADE_HEADLESS，本机没有 EGL，headless 会直接 ImportError
os.environ.pop("ARCADE_HEADLESS", None)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import arcade
import arcade.resources

arcade.resources.add_resource_handle("assets", str(ROOT / "assets"))

import src.core.settings as settings
from src.core.settings import (ACTION_POINT_PER_TURN, ENEMY_ACTION_DELAY,
                               ENEMY_ANIM_TIME, TURN_END_DELAY)
from src.core.game_window import GameWindow
from src.core.resource_manager import res_manager
from src.core.status_manager import status_manager
from src.core.illustration_manager import illu_manager
from src.core.plot_manager import plot_manager, Plot
from src.core.combat_manager import combat_manager, TurnPhase
from src.objects.character import Character
from src.objects.deck import Deck
from src.objects.combat_show import CombatShow
from src.objects.status_block import StatusBlock
from src.tools.timer import Timer

results = []


def check(name: str, ok: bool, detail: str = ""):
    results.append((name, ok, detail))


def raises(fn, exc) -> bool:
    try:
        fn()
    except exc:
        return True
    except Exception:
        return False
    return False


# 唯一窗口：真实游戏尺寸。会短暂显示一个窗口（隐藏窗口下截不到内容）
window = GameWindow(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, "verify")

# ---------------------------------------------------------------- A6
attack_cls = res_manager.effect("attack")
defense_cls = res_manager.effect("defense")
mucus_cls = res_manager.effect("mucus")

check("A6 attack -> AttackEffect", attack_cls.__name__ == "AttackEffect", attack_cls.__name__)
check("A6 defense -> DefenseEffect", defense_cls.__name__ == "DefenseEffect", defense_cls.__name__)
check("A6 mucus -> MucusEffect", mucus_cls.__name__ == "MucusEffect", mucus_cls.__name__)
check("A6 缓存命中同一个类", res_manager.effect("attack") is attack_cls)
check("A6 未知效果名报错", raises(lambda: res_manager.effect("no_such_effect"), FileNotFoundError))

# ---------------------------------------------------------------- B5
char = Character("meowm")
globals()["_CHAR"] = char
atk_card = next(c for c in char.cards if c.type == "attack")
check("B5 攻击卡效果为四元组", len(atk_card.effects[0]) == 4)
check("B5 缺省参数为空字典", atk_card.effects[0][3] == {})
check("B5 效果类已解析", atk_card.effects[0][0] is attack_cls)
def_card = next(c for c in char.cards if c.type == "skill")
check("B5 防御卡效果类正确", def_card.effects[0][0] is defense_cls)

# ---------------------------------------------------------------- A2 / B4
foe = Character("grassland_slime")
hp0 = foe.hp
foe.hp = foe.hp - 6
check("A2 扣血正常", foe.hp == hp0 - 6, f"hp={foe.hp}")
check("B4 无护盾掉血 -> is_hurt", foe.is_hurt is True)

foe2 = Character("grassland_slime")
foe2.shield = 10
foe2.hp = foe2.hp - 6
check("B4 护盾完全挡下不算被打到", foe2.is_hurt is False and foe2.shield == 4,
      f"hp={foe2.hp} shield={foe2.shield}")
foe2.hp = foe2.hp - 10
check("B4 护盾被击穿算被打到", foe2.is_hurt is True and foe2.shield == 0.0)

foe3 = Character("grassland_slime")
foe3.hp = 0
check("A2 血量归零即死亡", foe3.death is True and foe3.alive is False and foe3.hp == 0)

# ---------------------------------------------------------------- C1
deck = Deck(char, settings.SCREEN_WIDTH / 2, 0)
for _ in range(5):
    deck.update_card()
check("C1 parts 不随重建立累积", len(deck.parts) <= len(char.hand),
      f"parts={len(deck.parts)} hand={len(char.hand)}")

# ---------------------------------------------------------------- B3
enemy = [Character("grassland_slime"), Character("grassland_slime"), Character("grassland_slime")]
enemy[1].death = True
combat_manager.combat = [[char], enemy]
combat_manager.update()
check("B3 死亡敌人被清理", len(combat_manager.enemy) == 2, f"len={len(combat_manager.enemy)}")
check("B3 列表对象保持同一性", combat_manager.enemy is enemy)

dummy = Character("grassland_slime")
globals()["_DUMMY"] = dummy
dummy.effects.append(attack_cls(dummy, 6))
status_manager.team = [char]
status_manager.enemy = [dummy]
status_manager.check_effect()
check("B3 一次性效果立即出列", dummy.effects == [] and dummy.hp == dummy.max_hp - 6,
      f"effects={len(dummy.effects)} hp={dummy.hp}")

# ---------------------------------------------------------------- B4 复位 + MucusEffect
status_manager.team = [char]
status_manager.enemy = [dummy]
char.is_hurt = True
status_manager.on_turn_start("team")
check("B4 队伍回合开始复位 is_hurt", char.is_hurt is False)
char.is_hurt = True
status_manager.on_turn_start("enemy")
check("B4 敌人回合开始不复位队伍的 is_hurt", char.is_hurt is True)

char.effects = [mucus_cls(char, 1)]
char.hand.clear()
char.is_hurt = True
status_manager.on_turn_end("enemy")
check("B4 粘液效果在敌方回合结束发牌",
      len(char.hand) == 1 and char.hand[0].data["name"] == "粘液" and char.effects == [],
      f"hand={len(char.hand)} effects={len(char.effects)}")

char.effects = [mucus_cls(char, 1)]
char.hand.clear()
char.is_hurt = False
status_manager.on_turn_end("enemy")
check("B4 没挨打则不发牌", len(char.hand) == 0)

# ---------------------------------------------------------------- B1
poor = Character("meowm")
poor.action_point = 0
card0 = poor.cards[0]
check("B1 行动点不足返回 False", card0.use_card() is False)
check("B1 费用不足时卡牌仍在手牌", card0 not in poor.discard_pile)
deck_b1 = Deck(poor, 800, 0)
deck_b1.selected = None                              # 没选中时清空选中不该崩
check("B1 未选中时清空选中安全", deck_b1.selected is None)
deck_b1.selected = card0
deck_b1.selected = None
check("B1 取消选中后不再持有卡牌", deck_b1.selected is None and card0 not in poor.discard_pile)

# 敌人全灭后再点攻击牌不能崩（此前是 IndexError）
loader = Character("meowm")
loader.action_point = 10
atk = next(c for c in loader.cards if c.type == "attack")
status_manager.enemy = []
check("B1 无敌人时攻击牌 valid_targets 为 False", atk.valid_targets() is False)
check("B1 无敌人时攻击牌不受理", atk.use_card() is False)
deck_b2 = Deck(loader, 800, 0)
deck_b2.selected = atk
deck_b2.selected = atk        # 第二次点击 = 试图打出
check("B1 无敌人时重复点击不抛异常", deck_b2.selected is atk)
status_manager.enemy = [Character("grassland_slime")]

# ---------------------------------------------------------------- A4
enemies = [Character("grassland_slime"), Character("grassland_slime")]
illu_manager.combat = [[char], enemies]
status_manager.combat = [[char], enemies]        # 指针是按 manager 的列表算的，必须与块一致
show = CombatShow([char], enemies)
blocks = len(show.enemy_chars)
enemies[0].death = True
for _ in range(200):
    show.update(1 / 60)
check("A4 死亡块淡出", show.enemy_chars[0].fade == 0.0 and show.enemy_chars[0].visible is False,
      f"fade={show.enemy_chars[0].fade}")
check("A4 死亡块保留槽位", len(show.enemy_chars) == blocks and len(show.enemy_status) == blocks)
check("A4 指针指向存活单位", status_manager.enemy_ptr == 1, f"ptr={status_manager.enemy_ptr}")
check("A4 存活单位未被淡出", show.enemy_chars[1].fade == 1.0)
char.death = True
for _ in range(200):
    show.update(1 / 60)
check("A4 队伍块也会淡出", show.team_chars[0].fade == 0.0)
check("A4 状态栏整体随淡出隐藏", show.team_status[0].fade == 0.0 and show.team_status[0].visible is False)
show.team_status[0].draw()          # 数字不是 sprite，靠 draw 时同步透明度
check("A4 数字渲染器跟随淡出", show.team_status[0].hp_text.fade == 0.0)

# ---------------------------------------------------------------- C3
plot_manager.delegate = [
    Plot(arcade.Text("a", 0, 0), Timer(1.0), mode="follow"),
    Plot(arcade.Text("b", 0, 0), Timer(1.0), mode="follow"),
]
plot_manager.update(0.1)
check("C3 follow 独占屏幕", len(plot_manager.show) == 1, f"show={len(plot_manager.show)}")
plot_manager.delegate = [
    Plot(arcade.Text("a", 0, 0), Timer(1.0), mode="meantime"),
    Plot(arcade.Text("b", 0, 0), Timer(1.0), mode="follow"),
]
plot_manager.update(0.1)
check("C3 meantime 与 follow 并行", len(plot_manager.show) == 2, f"show={len(plot_manager.show)}")
plot_manager.update(2.0)
check("C3 过期提示被移除", plot_manager.delegate == [] and plot_manager.show == [])

# ---------------------------------------------------------------- B7 敌人独立技能通道
from src.objects.skill import SkillEntry

foe4 = Character("grassland_slime")
player = Character("meowm")
status_manager.combat = [[player], [foe4]]
entry = foe4.skills[0]
check("B7 技能条目带意图与技能名", entry.intention == "attack" and entry.name == "mucus_strike",
      f"intention={entry.intention} name={entry.name}")
check("B7 技能条目兼容字典式访问", entry['skill'] is entry.card and entry['intention'] == "attack")

hp_before = player.hp
ap_before = foe4.action_point
check("B7 敌人行动点为 0", ap_before == 0)
check("B7 cast() 成功", entry.cast() is True)
check("B7 不看行动点也能造成伤害", player.hp == hp_before - 6, f"hp {hp_before} -> {player.hp}")
check("B7 不消耗行动点", foe4.action_point == ap_before, f"ap={foe4.action_point}")
check("B7 技能不进入手牌/弃牌堆",
      len(foe4.hand) == 0 and len(foe4.discard_pile) == 0 and entry.card not in foe4.discard_pile)

# 技能轮转：走完整回合（状态机驱动）后意图与队列都要跟着走
def run_full_turn(accelerate: bool = True, max_steps: int = 200) -> int:
    """从 PLAYER 阶段推进到下一个 PLAYER 阶段，返回经过的 update 次数。"""
    if combat_manager.phase is TurnPhase.ROUND_START:
        combat_manager.update(1 / 60)            # 先把开场提示/抽牌走完
    assert combat_manager.request_end_turn(), "当前阶段不接受结束回合"
    steps = 0
    while steps < max_steps:
        if accelerate:
            combat_manager.phase_time = 1e9     # 跳过停顿，只验证流程
            combat_manager.action_timer = 1e9
        combat_manager.update(1 / 60)
        steps += 1
        if combat_manager.phase is TurnPhase.PLAYER:
            return steps
    raise AssertionError("回合没有回到 PLAYER 阶段")


foe5 = Character("grassland_slime")
player2 = Character("meowm")
status_manager.combat = [[player2], [foe5]]
combat_manager.combat = [[player2], [foe5]]
intentions = [foe5.intention]
for _ in range(3):
    run_full_turn()
    intentions.append(foe5.intention)
check("B7 技能队列轮转", all(i == "attack" for i in intentions), f"{intentions}")
check("B7 轮转后队列长度不变", len(foe5.skills) == len(foe5.data['skills']), f"len={len(foe5.skills)}")
check("B7 轮转后仍兼容旧取法", foe5.skills[0]['intention'] == "attack")
check("B7 三个回合后回合数正确", combat_manager.round == 4, f"round={combat_manager.round}")

# 目标全灭时不出手
foe6 = Character("grassland_slime")
status_manager.combat = [[], [foe6]]
check("B7 玩家全灭时 valid_targets 为 False", foe6.skills[0].valid_targets() is False)
check("B7 玩家全灭时 cast() 返回 False", foe6.skills[0].cast() is False)
check("B7 玩家全灭时不产生效果", len(foe6.effects) == 0)

# 已倒下的敌人不再出手
foe7 = Character("grassland_slime")
player3 = Character("meowm")
status_manager.combat = [[player3], [foe7]]
combat_manager.combat = [[player3], [foe7]]
foe7.death = True
hp3 = player3.hp
run_full_turn()
check("B7 死亡敌人不出手", player3.hp == hp3, f"hp {hp3} -> {player3.hp}")

# ---------------------------------------------------------------- B8 回合状态机
foe8 = Character("grassland_slime")
foe9 = Character("grassland_slime")
player4 = Character("meowm")
status_manager.combat = [[player4], [foe8, foe9]]
combat_manager.combat = [[player4], [foe8, foe9]]

check("B8 初始为 ROUND_START 阶段", combat_manager.phase is TurnPhase.ROUND_START)
combat_manager.update(1 / 60)
check("B8 抽牌后进入 PLAYER 阶段", combat_manager.phase is TurnPhase.PLAYER)
check("B8 进入 PLAYER 时已抽牌", len(player4.hand) == 4, f"hand={len(player4.hand)}")
check("B8 PLAYER 阶段允许操作", combat_manager.can_act is True)

check("B8 结束回合受理", combat_manager.request_end_turn() is True)
check("B8 转入 PLAYER_END 阶段", combat_manager.phase is TurnPhase.PLAYER_END)
check("B8 PLAYER_END 阶段禁止操作", combat_manager.can_act is False)
check("B8 非 PLAYER 阶段重复请求被拒", combat_manager.request_end_turn() is False)

# 停顿未到时不应该结算
combat_manager.update(0.1)
check("B8 停顿未到不结算", combat_manager.phase is TurnPhase.PLAYER_END)
# 停顿到时：弃手牌并转入敌人阶段
combat_manager.update(TURN_END_DELAY)
check("B8 停顿结束转入 ENEMY 阶段", combat_manager.phase is TurnPhase.ENEMY, f"phase={combat_manager.phase}")
check("B8 手牌已弃掉", len(player4.hand) == 0, f"hand={len(player4.hand)}")

hp_before_enemy = player4.hp
# 敌人逐个出手：每次出手之间都要有间隔
combat_manager.update(ENEMY_ACTION_DELAY)
check("B8 第一个敌人先出手", player4.hp == hp_before_enemy - 6, f"hp={player4.hp}")
combat_manager.update(0.01)
check("B8 间隔未到第二个敌人不出手", player4.hp == hp_before_enemy - 6, f"hp={player4.hp}")
combat_manager.update(ENEMY_ACTION_DELAY)
check("B8 第二个敌人随后出手", player4.hp == hp_before_enemy - 12, f"hp={player4.hp}")

combat_manager.update(1 / 60)
check("B8 敌人出完转入 ENEMY_END", combat_manager.phase is TurnPhase.ENEMY_END, f"phase={combat_manager.phase}")
combat_manager.update(1 / 60)
check("B8 收尾后回到 ROUND_START 且回合数 +1",
      combat_manager.phase is TurnPhase.ROUND_START and combat_manager.round == 2,
      f"phase={combat_manager.phase} round={combat_manager.round}")
combat_manager.update(1 / 60)
check("B8 新回合回到 PLAYER 并至少抽满 4 张",
      combat_manager.phase is TurnPhase.PLAYER and len(player4.hand) >= 4,
      f"phase={combat_manager.phase} hand={len(player4.hand)}")
check("B8 新回合行动点已重置", player4.action_point == ACTION_POINT_PER_TURN,
      f"ap={player4.action_point}")

# 敌人出手时切了攻击立绘
foe10 = Character("grassland_slime")
player5 = Character("meowm")
status_manager.combat = [[player5], [foe10]]
illu_manager.combat = [[player5], [foe10]]
combat_manager.combat = [[player5], [foe10]]
combat_manager.update(1 / 60)
combat_manager.request_end_turn()
combat_manager.update(TURN_END_DELAY)
combat_manager.update(ENEMY_ACTION_DELAY)
check("B8 敌人出手切换攻击立绘", len(illu_manager.delegate) > 0, f"delegate={len(illu_manager.delegate)}")

# ---------------------------------------------------------------- 血条几何（回归）
def _vis(sprite):
    w = sprite.width
    return (min(sprite.center_x + w / 2, sprite.center_x - w / 2),
            max(sprite.center_x + w / 2, sprite.center_x - w / 2))


for side, on_left, bx in (("我方", True, 15), ("敌方", False, 1300)):
    foe_bar = Character("grassland_slime")
    illu_manager.combat = [[foe_bar], []] if on_left else [[], [foe_bar]]
    block = StatusBlock(bx, 0, foe_bar, avatar_on_left=on_left)
    inner0 = _vis(block.hp_bar)[0] + StatusBlock.BAR_INNER_LEFT_PX * block.hp_bar_size
    inner1 = inner0 + (StatusBlock.BAR_INNER_RIGHT_PX - StatusBlock.BAR_INNER_LEFT_PX) * block.hp_bar_size
    # 可调微调量：血条锚定端按 inset 朝内收（单位是素材像素）
    inset = (StatusBlock.BAR_INSET_PX if on_left else StatusBlock.ENEMY_BAR_INSET_PX) \
        * block.hp_bar_size
    clip0, clip1 = inner0 + (0 if on_left else -inset), inner1 - (inset if on_left else 0)
    inside_all = True
    anchor_all = True
    width_all = True
    for ratio in (1.0, 0.75, 0.5, 0.25, 0.05):
        foe_bar._hp = foe_bar.max_hp * ratio
        block.update()
        block.update_position()
        b0, b1 = _vis(block.bar)
        inside_all = inside_all and b0 >= clip0 - 2.5 and b1 <= clip1 + 2.5
        # 心形在原图左侧：我方贴内腔左沿，敌方整块镜像后表现为贴内腔右沿
        anchor = inner0 + inset if on_left else inner1 - inset
        anchor_all = anchor_all and abs((b0 if on_left else b1) - anchor) <= 2.5
        width_all = width_all and abs(abs(block.bar.width) -
                                      block.bar_full_width * ratio) < 0.5
    check("血条 %s 始终落在框内腔里" % side, inside_all)
    check("血条 %s 贴住心形同侧一端" % side, anchor_all,
          "左沿对齐" if on_left else "右沿对齐")
    # 数字必须落在贴图范围内（镜像时曾经被推到贴图外）
    tex0 = _vis(block.hp_bar)[0]
    tex1 = tex0 + block.hp_bar.width * (1 if block.hp_bar.width > 0 else -1)
    hp_x = block.hp_text.position[0]
    check("血量数字 %s 落在贴图范围内" % side, min(tex0, tex1) <= hp_x <= max(tex0, tex1),
          f"数字 x={hp_x:.1f} 贴图=[{min(tex0, tex1):.1f},{max(tex0, tex1):.1f}]")

# 满血时应恰好铺满内腔
foe_bar._hp = foe_bar.max_hp
block.update()
block.update_position()
check("血条满血宽度等于内腔宽度",
      abs(abs(block.bar.width) - block.bar_full_width) < 0.5,
      f"bar={abs(block.bar.width):.1f}")

# ---------------------------------------------------------------- 立绘/动画（回归）
# 打掉一个敌人后，剩下的敌人必须还能拿到“攻击”立绘（曾经会串到已倒下者的槽位）
ally = Character("meowm")
foes = [Character("grassland_slime"), Character("grassland_slime")]
illu_manager.combat = [[ally], foes]
status_manager.combat = [[ally], foes]
combat_manager.combat = [[ally], foes]
show2 = CombatShow([ally], foes)
combat_manager.update(1 / 60)                 # 走完开场 ROUND_START
foes[0].hp = 0                                # 击倒第一个
combat_manager.request_end_turn()
for _ in range(400):
    combat_manager.update(1 / 60)
    show2.update(1 / 60)
    illu_manager.update(1 / 60)
    status_manager.update_ptr()
    if combat_manager.phase is TurnPhase.PLAYER:
        break

survivor_block = show2.enemy_chars[1]
dead_block = show2.enemy_chars[0]
check("立绘 存活敌人拿到攻击立绘", survivor_block.illu_key == "attack",
      f"key={survivor_block.illu_key}")
check("立绘 已倒下敌人不再占用攻击立绘", dead_block.illu_key != "attack",
      f"key={dead_block.illu_key}")
check("立绘 立绘表随列表重排", len(illu_manager.enemy_illu) == len(illu_manager.enemy) == 1,
      f"illu={len(illu_manager.enemy_illu)} list={len(illu_manager.enemy)}")
check("立绘 存活的块拿到的就是自己那份字典",
      survivor_block.illu_illu is illu_manager.enemy_illu[0])

# 再走一回合，动画仍要出现
combat_manager.request_end_turn()
anim_frames = 0
for _ in range(400):
    combat_manager.update(1 / 60)
    show2.update(1 / 60)
    illu_manager.update(1 / 60)
    status_manager.update_ptr()
    if any(d['illu'] == 'attack' for d in illu_manager.delegate):
        anim_frames += 1
    if combat_manager.phase is TurnPhase.PLAYER:
        break
check("立绘 下一回合仍有出手动画", anim_frames > 0, f"frames={anim_frames}")

# ---------------------------------------------------------------- 集成：多回合跑动 + 绘制
try:
    # 让场景自己装配（Combat 在 auto_register 时构造，会重新注入各 manager）
    window.auto_register(ROOT / "src" / "scenes")
    window.switch_scene("combat")
    combat = window.get_scene("combat")
    combat.on_show_view()
    window.dispatch_events()

    player = combat.character[0]                 # 用场景自己的角色，避免和前面的用例混淆
    check("集成 敌人意图已初始化",
          all(c.intention is not None for c in combat.imagine_enemy))
    hp_start = player.hp

    def wait_for_player(max_frames: int = 1200) -> bool:
        """跑帧直到回到 PLAYER 阶段（而不是固定帧数，避免时序假设）。"""
        for _ in range(max_frames):
            combat.on_update(1 / 60)
            combat.on_draw()
            if combat_manager.can_act:
                return True
        return False

    turns_ok = 0
    for _ in range(4):
        combat.on_key_press(arcade.key.G, 0)     # 结束回合 -> 敌人行动 + 新回合
        if wait_for_player():
            turns_ok += 1
    window.flip()

    check("集成 4 个回合都能走完并回到玩家阶段", turns_ok == 4, f"turns={turns_ok}")
    check("集成 多回合更新+绘制不抛异常", True)
    check("集成 敌人行动造成了伤害", player.hp < hp_start, f"hp {hp_start} -> {player.hp}")
    check("集成 手牌已发放", len(combat.deck.hand) > 0, f"hand={len(combat.deck.hand)}")
    check("集成 回合数递增", combat_manager.round >= 4, f"round={combat_manager.round}")
    check("集成 战斗仍标记为进行中", combat_manager.combat is True)

    # 敌人全灭后不该崩
    for c in combat.imagine_enemy:
        c.hp = 0
    for _ in range(30):
        combat.on_update(1 / 60)
        combat.on_draw()
    check("集成 敌人全灭后继续运行", True)
except Exception as e:
    import traceback
    traceback.print_exc()
    check("集成 多回合更新+绘制不抛异常", False, f"{type(e).__name__}: {e}")

# ---------------------------------------------------------------- 场景移植（回归）
try:
    from src.core.app_state import app_state
    from src.core.game_data import list_characters

    expected_scenes = ["menu", "archive", "character", "prepare", "action", "settings"]
    for name in expected_scenes:
        check(f"场景 {name} 已注册", name in window.scenes)

    # 全流程：主页 -> 存档 -> 选角 -> 准备 -> 行动
    app_state.start_new_game(0)
    for name in expected_scenes:
        window.switch_scene(name)
        view = window.scenes[name]
        view.on_show_view()
        for _ in range(3):
            view.on_update(1 / 60)
            view.on_mouse_motion(1200, 450, 0, 0)
        view.on_draw()
    check("场景 全部可更新+绘制", True)

    # 存档卡片 -> 确认 -> 选角（走场景级事件分发，顺带验证点击不穿透）
    arc_scene = window.scenes["archive"]
    arc_scene.on_show_view()
    arc_scene.on_update(1 / 60)
    arrow = arc_scene.right_btn
    arc_scene.on_mouse_press(int(arrow.x), int(arrow.y), 1, 0)
    arc_scene.on_mouse_release(int(arrow.x), int(arrow.y), 1, 0)
    check("存档 点右箭头不会穿透触发下面的卡片",
          not arc_scene.messagebox.visible and arc_scene.roulette.pointer == 1,
          f"dialog={arc_scene.messagebox.visible} ptr={arc_scene.roulette.pointer}")

    card = arc_scene.roulette.items[1]
    arc_scene.on_mouse_press(int(card.x), int(card.y), 1, 0)
    arc_scene.on_mouse_release(int(card.x), int(card.y), 1, 0)
    check("存档 点击存档位弹出确认框", arc_scene.messagebox.visible)
    arc_scene.messagebox.close(True)
    check("存档 确认后切到选角", arc_scene._pending_scene == "character",
          f"pending={arc_scene._pending_scene}")
    check("存档 写入当前存档位", app_state.current_archive == 1,
          f"slot={app_state.current_archive}")

    # 选角
    char_scene = window.scenes["character"]
    char_scene.on_show_view()
    char_scene.on_update(1 / 60)
    check("选角 至少有一个可选角色", len(list_characters()) >= 1,
          f"{list_characters()}")
    ccard = char_scene.roulette.items[0]
    char_scene.on_mouse_press(int(ccard.x), int(ccard.y), 1, 0)
    char_scene.on_mouse_release(int(ccard.x), int(ccard.y), 1, 0)
    char_scene.messagebox.close(True)
    check("选角 确认后切到准备", char_scene._pending_scene == "prepare")
    check("选角 记录当前角色", bool(app_state.current_character),
          f"{app_state.current_character}")

    # 准备 -> 选模式
    prep = window.scenes["prepare"]
    prep.on_show_view()
    prep.on_update(1 / 60)
    btn = prep.mode_buttons[0]
    prep.on_mouse_press(int(btn.x), int(btn.y), 1, 0)
    prep.on_mouse_release(int(btn.x), int(btn.y), 1, 0)
    prep.messagebox.close(True)
    check("准备 确认后切到行动", prep._pending_scene == "action",
          f"pending={prep._pending_scene}")
    check("准备 模式已写入", app_state.game_mode == 0)
    check("准备 存档已落盘", app_state.has_archive(app_state.current_archive))

    # 行动 -> 战斗
    act = window.scenes["action"]
    act.on_show_view()
    act.on_update(1 / 60)
    bcard = act.roulette.items[0]
    act.on_mouse_press(int(bcard.x), int(bcard.y), 1, 0)
    act.on_mouse_release(int(bcard.x), int(bcard.y), 1, 0)
    act.messagebox.close(True)
    check("行动 确认后切到战斗", act._pending_scene == "combat",
          f"pending={act._pending_scene}")

    # 战斗回流：敌人全灭后自动回到行动界面，并能再次开战
    window.switch_scene("combat")
    fight = window.scenes["combat"]
    fight.on_show_view()
    fight.on_update(1 / 60)
    for foe in list(combat_manager.enemy):
        foe.hp = 0
    for _ in range(240):
        fight.on_update(1 / 60)
    check("战斗 敌人全灭后自动回到行动界面", fight._returning is True)
    fight.on_show_view()
    check("战斗 再次进入会重新开一场",
          len(combat_manager.enemy) == 2 and fight._returning is False,
          f"enemies={len(combat_manager.enemy)} returning={fight._returning}")

    # 设置：音量加减与持久化
    setting = window.scenes["settings"]
    setting.on_show_view()
    before = app_state.volume
    setting.on_mouse_press(int(setting.plus_btn.x), int(setting.plus_btn.y), 1, 0)
    setting.on_mouse_release(int(setting.plus_btn.x), int(setting.plus_btn.y), 1, 0)
    check("设置 音量 +10", app_state.volume == min(100, before + 10),
          f"{before} -> {app_state.volume}")
    app_state.volume = before
    app_state.save_settings()

    # 存档读回
    app_state.reload()
    check("存档 能读回刚写入的内容", app_state.has_archive(app_state.current_archive))
    app_state.delete_archive(app_state.current_archive)
except Exception as e:
    import traceback
    traceback.print_exc()
    check("场景 移植回归", False, f"{type(e).__name__}: {e}")

# ---------------------------------------------------------------- 汇总
failed = [r for r in results if not r[1]]
for name, ok, detail in results:
    print(f"[{'OK  ' if ok else 'FAIL'}] {name}" + (f"   ({detail})" if detail else ""))
print(f"\n{len(results) - len(failed)}/{len(results)} passed")
sys.exit(1 if failed else 0)
