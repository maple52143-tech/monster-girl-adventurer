from pathlib import Path
import os
import arcade

from src.core.resource_manager import res_manager


class Card(arcade.Sprite):
    def __init__(self, name: str, owner):
        t, self.data = res_manager.card(name)
        super().__init__(t, 0.13)

        self.owner = owner
        self.effects = []
        for name, value in self.data['effect'].items():
            self.effects.append(res_manager.effect(name)(value))

    def use(self, owner, other):
