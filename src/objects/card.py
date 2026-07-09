import arcade

from src.core.resource_manager import res_manager

class Card(arcade.Sprite):
    def __init__(self, name: str):
        t, self.data = res_manager.card(name)
        super().__init__(t, 0.1)