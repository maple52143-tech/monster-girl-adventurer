from enum import Enum

from src.core.illustration_manager import illu_manager
from src.core.plot_manager import plot_manager
from src.core.settings import (ACTION_POINT_PER_TURN, ENEMY_ACTION_DELAY,
                               ENEMY_ANIM_TIME, HAND_SIZE, TURN_END_DELAY)
from src.core.status_manager import status_manager

from src.tools.random_things import pop_random


class TurnPhase(Enum):
    """回合阶段。只有 PLAYER 阶段接受出牌与结束回合操作。"""
    ROUND_START = "round_start"     # 展示回合提示 + 抽牌
    PLAYER = "player"               # 玩家可操作
    PLAYER_END = "player_end"       # 玩家已结束回合，等待结算
    ENEMY = "enemy"                 # 敌人逐个出手
    ENEMY_END = "enemy_end"         # 敌方回合收尾


class CombatManager:
    def __init__(self):
        self.team: list = []
        self.enemy: list = []
        self.is_combat = False

        # 局内游戏数据
        self.round = 0
        self.phase = None
        self.phase_time = 0.0        # 当前阶段已停留时间
        self.action_timer = 0.0      # 敌人出手间隔计时
        self.enemy_index = 0         # 当前要出手的敌人下标

    @property
    def combat(self):
        return self.is_combat

    @combat.setter
    def combat(self, value):
        self.is_combat = True
        self.team = value[0]
        self.enemy = value[1]
        self.round = 1
        self.phase = TurnPhase.ROUND_START
        self.phase_time = 0.0
        self.action_timer = 0.0
        self.enemy_index = 0

        for c in self.team:
            c.draw_pile = c.cards[:]
            c.hand.clear()
            c.discard_pile = []
            c.action_point = ACTION_POINT_PER_TURN
        for who in self.enemy:
            who.intention = who.skills[0]['intention']

    @combat.deleter
    def combat(self):
        self.is_combat = False
        self.team = []
        self.enemy = []
        self.round = 0
        self.phase = None
        self.phase_time = 0.0
        self.action_timer = 0.0
        self.enemy_index = 0

    # ------------------------------------------------------------ 阶段查询

    @property
    def can_act(self) -> bool:
        """玩家现在能不能出牌 / 选目标。"""
        return self.is_combat and self.phase is TurnPhase.PLAYER

    def request_end_turn(self) -> bool:
        """玩家请求结束回合。只有 PLAYER 阶段受理，受理后转入结算。"""
        if not self.can_act:
            return False
        self._enter_phase(TurnPhase.PLAYER_END)
        return True

    # ------------------------------------------------------------ 主循环

    def update(self, delta_time: float = 1 / 60):
        if not self.is_combat:
            return

        self._clear_dead_enemies()
        if not self.enemy:
            self.on_combat_end()

        self.phase_time += delta_time
        self.action_timer += delta_time

        match self.phase:
            case TurnPhase.ROUND_START:
                self._phase_round_start()
            case TurnPhase.PLAYER:
                pass                                        # 等玩家操作
            case TurnPhase.PLAYER_END:
                self._phase_player_end()
            case TurnPhase.ENEMY:
                self._phase_enemy()
            case TurnPhase.ENEMY_END:
                self._phase_enemy_end()

    # ------------------------------------------------------------ 各阶段

    def _enter_phase(self, phase: TurnPhase):
        self.phase = phase
        self.phase_time = 0.0

    def _phase_round_start(self):
        # 回合提示与抽牌同时发生，提示的存活时长由 PlotManager 自己管
        plot_manager.title(f"第{self.round}回合", 1.0)
        for who in self.team:
            # 补到手牌上限，而不是无条件再加 HAND_SIZE 张：
            # 否则敌人塞进来的粘液牌会挤占抽牌位（手牌会变成 5、6 张往上堆）
            self.draw_cards(HAND_SIZE - len(who.hand), who)
        for who in self.team:
            who.action_point = ACTION_POINT_PER_TURN
        self._enter_phase(TurnPhase.PLAYER)

    def _phase_player_end(self):
        if self.phase_time < TURN_END_DELAY:
            return
        # 队伍回合结束的钩子（粘液等“敌方回合结束触发”的状态在敌人收尾时结算）
        status_manager.on_turn_end("team")
        for who in self.team:
            who.discard_pile.extend(who.hand[:])
            who.hand.clear()
        status_manager.on_turn_start("enemy")
        self.enemy_index = 0
        self.action_timer = ENEMY_ACTION_DELAY
        self._enter_phase(TurnPhase.ENEMY)

    def _phase_enemy(self):
        while self.enemy_index < len(self.enemy) and self.enemy[self.enemy_index].death:
            self.enemy_index += 1                       # 已倒下的跳过

        if self.enemy_index >= len(self.enemy):
            self._enter_phase(TurnPhase.ENEMY_END)      # 都出完手了，立刻收尾
            return

        if self.action_timer < ENEMY_ACTION_DELAY:
            return
        self.action_timer = 0.0

        who = self.enemy[self.enemy_index]
        entry = who.skills.popleft()
        illu_manager.change_illu("no", who, ENEMY_ANIM_TIME, "attack")
        entry.cast()                                    # 独立通道：不看行动点，不入手牌
        who.skills.append(entry)
        who.intention = who.skills[0].intention
        self.enemy_index += 1

    def _phase_enemy_end(self):
        status_manager.on_turn_end("enemy")             # 队伍身上的“敌方回合结束”状态在这结算
        self.round += 1
        status_manager.on_turn_start("team")
        self._enter_phase(TurnPhase.ROUND_START)

    # ------------------------------------------------------------ 杂项

    def _clear_dead_enemies(self):
        alive = [c for c in self.enemy if not c.death]
        if len(alive) == len(self.enemy):
            return
        self.enemy[:] = alive               # 原地替换，保持各 manager 持有的是同一个列表
        # 列表缩短后立绘槽位必须同步重排，否则存活单位会拿到别人的（或已倒下者的）
        # 立绘槽位，表现为“打掉一个之后剩下的敌人不再播出手动画”
        illu_manager.remove_dead(self.team, self.enemy)

    def draw_cards(self, num: int, who):
        for _ in range(num):
            if not who.draw_pile and not who.discard_pile:
                return
            if not who.draw_pile:
                who.draw_pile = who.discard_pile[:]
                who.discard_pile = []

            who.hand.append(pop_random(who.draw_pile))

    def on_combat_end(self):
        pass

    # ------------------------------------------------------------ 兼容旧调用

    def new_round(self):
        """兼容旧调用：等价于「结束玩家回合 + 立刻把状态机推到下一步」。

        现在整条时间线由 update() 驱动，所以调用方需要继续调用 update()。
        """
        self.request_end_turn()
        self.phase_time = 1e9
        self.action_timer = 1e9


combat_manager = CombatManager()
