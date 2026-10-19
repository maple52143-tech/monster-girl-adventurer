from psygnal.containers import EventedList
import arcade

from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.status_manager import status_manager
from src.core.illustration_manager import illu_manager

from src.objects.character_block import CharacterBlock
from src.objects.status_block import StatusBlock
from src.objects.character import Character

class CombatShow:
    def __init__(self, team: EventedList[Character], enemy: EventedList[Character]):
        self.team = team
        self.enemy = enemy

        # 立绘字典由每个块自己持有（按角色对象绑定），不受列表重排影响
        self.team_chars = [CharacterBlock(0, SCREEN_HEIGHT / 2, c, "team") for c in self.team]
        self.enemy_chars = [CharacterBlock(0, SCREEN_HEIGHT / 2, c, "enemy") for c in self.enemy]
        self.team_status = [StatusBlock(15, 0, c, avatar_on_left=True) for c in self.team]
        # 敌人状态栏整块镜像：头像与心形在右边，血条从右侧开始减少
        self.enemy_status = [StatusBlock(SCREEN_WIDTH - 300, 0, c, avatar_on_left=False)
                             for c in self.enemy]
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

    def update(self, delta_time: float = 1 / 60):
        # 死亡单位不删除块，只做淡出并保留槽位，这样块列表长度始终与角色列表一致
        fade_speed = 1.6          # 约 0.6 秒淡出完毕
        # 先把动画的临时立绘状态同步到各块（按角色对象匹配），再让块取图
        illu_manager.sync(self.team_chars + self.enemy_chars)
        for c in self.team_chars:
            self._fade_block(c, delta_time, fade_speed)
            c.update()
        for c in self.team_status:
            self._fade_block(c, delta_time, fade_speed)
            c.update()
            c.is_chosen = False
        status_manager.update_ptr()
        self.team_status[status_manager.team_ptr].is_chosen = True
        for c in self.enemy_chars:
            self._fade_block(c, delta_time, fade_speed)
            c.update()
        for c in self.enemy_status:
            self._fade_block(c, delta_time, fade_speed)
            c.update()
            c.is_chosen = False
        status_manager.update_ptr()
        self.enemy_status[status_manager.enemy_ptr].is_chosen = True

    @staticmethod
    def _fade_block(block, delta_time: float, speed: float):
        if not block.character.death:
            return
        block.fade = max(0.0, block.fade - delta_time * speed)
        block.visible = block.fade > 0.0

    def draw(self):
        for c in self.team_chars:
            c.draw()
        for c in self.team_status:
            c.draw()
        for c in self.enemy_chars:
            c.draw()
        for c in self.enemy_status:
            c.draw()