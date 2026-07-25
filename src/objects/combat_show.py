from psygnal.containers import EventedList
import arcade

from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.status_manager import status_manager

from src.objects.character_block import CharacterBlock
from src.objects.status_block import StatusBlock
from src.objects.character import Character

class CombatShow:
    def __init__(self, team: EventedList[Character], enemy: EventedList[Character]):
        self.team = team
        self.enemy = enemy

        self.team_chars = [CharacterBlock(0, SCREEN_HEIGHT / 2, c) for c in self.team]
        self.enemy_chars = [CharacterBlock(0, SCREEN_HEIGHT / 2, c) for c in self.enemy]
        self.team_status = [StatusBlock(0, 0, c) for c in self.team]
        self.enemy_status = [StatusBlock(SCREEN_WIDTH - 350, 0, c) for c in self.enemy]
        self._update_position()

    def select(self, x):
        if x < SCREEN_WIDTH / 2:
            t = len(self.team_chars) - 1 - int(x / (SCREEN_WIDTH / 2) * len(self.team_chars))
            status_manager.team_ptr = t if t < len(self.team_chars) else len(self.team_chars) - 1
        else:
            t = int((x - SCREEN_WIDTH / 2) / (SCREEN_WIDTH / 2) * len(self.enemy_chars))
            status_manager.enemy_ptr = t if t < len(self.enemy_chars) else len(self.enemy_chars) - 1

    def _update_position(self):
        dx = SCREEN_WIDTH / (2 * (len(self.team_chars) + 1))
        for i, c in enumerate(self.team_chars):
            c.x = SCREEN_WIDTH / 2 - dx * (i + 1)
        for i, c in enumerate(self.team_status):
            c.y = SCREEN_HEIGHT - i * c.size[1]

        dx = SCREEN_WIDTH / (2 * (len(self.enemy_chars) + 1))
        for i, c in enumerate(self.enemy_chars):
            c.x = SCREEN_WIDTH / 2 + dx * (i + 1)
        for i, c in enumerate(self.enemy_status):
            c.y = SCREEN_HEIGHT - i * c.size[1]

    def update(self):
        for c in self.team_chars:
            c.update()
        for c in self.team_status:
            c.update()
            c.is_chosen = False
        self.team_status[status_manager.team_ptr].is_chosen = True
        for c in self.enemy_chars:
            c.update()
        for c in self.enemy_status:
            c.update()
            c.is_chosen = False
        self.enemy_status[status_manager.enemy_ptr].is_chosen = True

    def draw(self):
        for c in self.team_chars:
            c.draw()
        for c in self.team_status:
            c.draw()
        for c in self.enemy_chars:
            c.draw()
        for c in self.enemy_status:
            c.draw()