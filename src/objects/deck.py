import math
import numpy as np
from psygnal.containers import SelectableEventedList
import arcade

from src.objects.standard import StandardSet
from src.objects.card import Card
from src.objects.character import Character
from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.tools.timer import Motion


def circle_calc(hand: SelectableEventedList[Card], delta_h: float, delta_w: float):
    if not hand:
        return np.array([])

    sum_width = sum([h.width for h in hand])
    sum_height = sum([h.height for h in hand])

    m = (sum_height / len(hand)) * delta_h * (1 - 1 / len(hand) + 0.05)
    up = (sum_height / len(hand)) * (delta_h + 0.5)
    x = (sum_width / len(hand)) * delta_w
    kx = (sum_width - (hand[0].width + hand[-1].width) / 2) * delta_w
    n = 0.25 * kx ** 2

    r = (n + m ** 2) / (2 * m)
    r = r if r > 400 else 400

    pos_and_angle = []

    ix = -kx / 2
    for i, h in enumerate(hand):
        iy = math.sqrt(r ** 2 - ix ** 2)
        angle = math.atan2(ix, iy) * 180 / math.pi
        pos_and_angle.append([ix, iy - (r - up), angle])
        ix += h.width * delta_w

    return np.array(pos_and_angle[:])

class Deck(StandardSet):
    def __init__(self, character: Character, x, y):
        super().__init__(x, y, "middle", "bottom", (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.card_width = 120
        self.card_height = 160
        self.character = character
        self.radius = 0

        self.card_pos: np.ndarray = None

        # self.character.hand.events.inserted.connect(self.update_card)
        # self.character.hand.events.removed.connect(self.update_card)
        self._selected: Card = None
        self._touched: Card = None

        self.update_card()

    @property
    def hand(self):
        return self.character.hand

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value: Card):
        if self._selected == value:
            self._selected.use_card()
            self._selected.init()
            self._selected = None
            return

        if self._selected is not None:
            self._selected.delegate.append(Motion(0.15, self._selected, "select_scale",
                                                  0.02, 0))
        if value is not None:
            value.delegate.append(Motion(0.15, value, "select_scale", 0, 0.02))

        self._selected = value

    @property
    def touched(self):
        return self._touched

    @touched.setter
    def touched(self, value):
        if self._touched == value:
            return

        if self._touched is not None:
            self._touched.delegate.append(Motion(0.1, self._touched, "touch_scale",0.01, 0))
        if value is not None:
            value.delegate.append(Motion(0.1, value, "touch_scale", 0, 0.01))

        self._touched = value

    def update(self, delta_time: float):
        for h in self.hand:
            h.update(delta_time)
        self.update_card()

    def update_card(self):
        self.card_pos = circle_calc(self.character.hand, 0.2, 0.8)
        self.sprites['default'].clear()
        for i, h in enumerate(self.character.hand):
            if h != self.selected:
                self.add_sprite(h, self.card_pos[i, 0], self.card_pos[i, 1], self.card_pos[i, 2])
        if self._selected is not None:
            i = self.character.hand.index(self._selected)
            self.add_sprite(self.character.hand[i], self.card_pos[i, 0], self.card_pos[i, 1], self.card_pos[i, 2])

        self.update_position()