import os
from collections import deque
from psygnal.containers import SelectableEventedList
import arcade

from src.core.resource_manager import res_manager
from src.objects.card import Card
from src.objects.skill import SkillEntry


class Character:
    def __init__(self, name):
        self.illustration = res_manager.image(f"illustration_{name}")
        self.combat_illu = {
            "normal": res_manager.image("normal", os.path.join("combat", name)),
            "attack": res_manager.image("attack", os.path.join("combat", name)),
            "low_health": res_manager.image("low_health", os.path.join("combat", name)),
        }
        self.avatar = res_manager.image(f"avatar_{name}")

        self.data, self.type = res_manager.data(name)
        self.name = self.data["name"]
        self.introduction = self.data["introduction"]

        self.max_hp = self.data['initial_status']['max_hp']
        self.max_mp = self.data['initial_status']['max_mp']
        self._hp = self.max_hp
        self._mp = self.max_mp / 2
        self.shield = 0.0
        self.action_point = 0
        self.effects = []
        self.cards: list[Card] = []
        self.discard_pile = []  # 弃牌堆
        self.hand: SelectableEventedList[Card] = SelectableEventedList()
        self.draw_pile = []  # 摸牌堆

        self.cards = [Card(i, self) for i in self.data['initial_deck']]
        self.draw_pile = self.cards[:]

        # 局内特殊数据
        self.is_hurt = False
        self.death = False

        # 敌人角色的出牌顺序和意图
        if self.type == 'enemy':
            self.skills = deque([SkillEntry(i['skill'], i['intention'], self)
                                 for i in self.data['skills']])
        self.intention = None

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        if value < self._hp:
            # 扣血：先用护盾抵扣，护盾挡下的部分不算“被打到”
            t = self._hp - value
            if t <= self.shield:
                self.shield -= t
            else:
                self._hp -= t - self.shield
                self.shield = 0.0
                self.is_hurt = True
        else:
            self._hp = value

        if self._hp <= 0:
            self._hp = 0
            self.on_death()

    @property
    def alive(self) -> bool:
        return not self.death

    @property
    def mp(self):
        return self._mp

    def on_death(self):
        self.death = True