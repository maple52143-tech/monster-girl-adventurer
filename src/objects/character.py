import arcade

from src.core.resource_manager import res_manager
from src.objects.card import Card


class Character:
    def __init__(self, name):
        self.illustration = res_manager.image(f"illustration_{name}")
        self.avatar = res_manager.image(f"avatar_{name}")

        self.data, self.type = res_manager.data(name)
        self.name = self.data["name"]
        self.introduction = self.data["introduction"]

        self.max_hp = self.data['initial_status']['max_hp']
        self.max_mp = self.data['initial_status']['max_mp']
        self._hp = self.max_hp
        self._mp = self.max_mp / 2
        self.effects = []
        self.cards: list[Card] = []
        self.discard_pile = []  # 弃牌堆
        self.hand: list[Card] = []
        self.draw_pile = []  # 摸牌堆

        self.cards = [Card(i, self) for i in self.data['initial_deck']]

        self.draw_pile = self.cards[:]
        self.hand = self.draw_pile[:]

        self.shield = 0.0

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        if value < 0 and self.type != "enemy":
            self._hp = 0
            self.on_death()
        else:
            self._hp = value

    def on_death(self):
        pass