import arcade
from src.objects.standard import StandardSet


class StatusBlock(StandardSet):
    def __init__(self, x: float, y: float, character):
        super().__init__(x, y, "left", "top", (400, 200))


