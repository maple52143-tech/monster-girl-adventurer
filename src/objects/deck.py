import math
import numpy as np
import arcade

from src.objects.standard import StandardSet
from src.objects.card import Card
from src.objects.character import Character
from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT


def circle_calc(hand: list[Card], delta_h: float, delta_w: float):
    if not hand:
        return np.array([])

    m = hand[0].height * delta_h
    up = hand[0].height * (delta_h + 0.5)
    x = hand[0].width * delta_w
    kx = (len(hand) - 1) * hand[0].width * delta_w
    n = 0.25 * kx ** 2

    r = (n + m ** 2) / (2 * m)

    pos_and_angle = []

    for i, h in enumerate(hand):
        ix = -kx / 2 + i * x
        iy = math.sqrt(r ** 2 - ix ** 2)
        angle = math.atan2(ix, iy) * 180 / math.pi
        pos_and_angle.append([ix, iy - (r - up), angle])

    return np.array(pos_and_angle[:])

class Deck(StandardSet):
    def __init__(self, character: Character, x, y):
        super().__init__(x, y, "middle", "bottom", (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.card_width = 120
        self.card_height = 160
        self.hand = character.hand
        self.radius = 0
        self.card_pos = circle_calc(self.hand, 0.2, 0.8)

        for i, h in enumerate(self.hand):
            self.add_sprite(h, self.card_pos[i, 0], self.card_pos[i, 1], self.card_pos[i, 2])

    def update(self):
        if self.is_moving:
            circle_calc(self.hand, 0.2, 0.8)