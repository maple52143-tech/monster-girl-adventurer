from psygnal.containers import SelectableEventedList

from src.core.plot_manager import plot_manager
from src.core.status_manager import status_manager

from src.tools.random_things import *

class CombatManager:
    def __init__(self):
        self.team: list = []
        self.enemy: list = []
        self.is_combat = False

        # 局内游戏数据
        self.round = 0
        self.next_round = True

    @property
    def combat(self):
        return self.is_combat

    @combat.setter
    def combat(self, value):
        self.is_combat = True
        self.team = value[0]
        self.enemy = value[1]
        self.round = 1
        self.next_round = True

        for c in self.team:
            c.draw_pile = c.cards[:]
            c.hand.clear()
            c.discard_pile = []
            c.action_point = 4
        for who in self.enemy:
            who.intention = who.skills[0]['intention']

    @combat.deleter
    def combat(self):
        self.is_combat = False
        self.team = []
        self.enemy = []
        self.round = 0

    def update(self):
        if not self.is_combat:
            return

        for c in self.enemy:
            if c.death:
                self.enemy.remove(c)

        if not self.enemy:
            self.on_combat_end()

        if self.next_round:
            plot_manager.title(f"第{self.round}回合", 1.0)
            self.next_round = False
            for who in self.team:
                self.draw_cards(4, who)

    def new_round(self):
        self.round += 1
        self.next_round = True
        status_manager.on_turn_end("team")
        status_manager.on_turn_start("enemy")
        for who in self.enemy:
            skill = who.skills.popleft()
            skill['skill'].use_card()
            who.skills.append(skill)
            who.intention = who.skills[0]['intention']
        status_manager.on_turn_end("enemy")
        status_manager.on_turn_start("team")
        for who in self.team:
            who.discard_pile.extend(who.hand[:])
            who.hand.clear()
            who.action_point = 4

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

combat_manager = CombatManager()