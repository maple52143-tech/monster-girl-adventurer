import arcade

from src.objects.standard import StandardSet
from src.objects.character import Character
from src.core.illustration_manager import illu_manager
from src.core.resource_manager import res_manager


class CharacterBlock(StandardSet):
    """场上的角色立绘 + 敌人意图图标。

    立绘字典（normal / attack / low_health）由本块自己持有：角色被移出战斗列表后
    索引会整体前移，靠索引反查会拿到别人（或已倒下者）的立绘，所以这里按角色对象
    绑定。illustration_manager 里那份表由它自己维护，表现层只按对象取。
    """

    def __init__(self, x, y, character: Character, illu_side: str = None):
        super().__init__(x, y, "left", "bottom", (200, 200))
        self.character = character
        # 记住自己在立绘列表里的槽位（用于 manager 同步动画状态）
        self.illu_side = illu_side or ("enemy" if character.type == "enemy" else "team")
        self.illu_illu, self.illu_key = illu_manager.attach(character, self.illu_side)
        if self.illu_illu is None:
            # 兜底：角色没在 manager 里注册（例如单独测试某个块）时自建一份
            self.illu_illu = {k: arcade.Sprite(character.combat_illu[k], scale=0.3)
                              for k in ('normal', 'attack', 'low_health')}
            self.illu_key = 'normal'

        self.sprites.add_sprite_list("intention")
        self.illu = self.current_illu()
        self.add_sprite(self.illu, 0, 0, 0)
        self.inten = {k: arcade.Sprite(res_manager.image(k, "intention"), 0.07) for k in
                      ['attack', 'defense', 'magic', 'move']}
        self.intention_shown = None

    def current_illu(self):
        """按当前状态取立绘；拿到的是本块自己的字典，不会再串到别的角色。"""
        return self.illu_illu[self.illu_key]

    def update(self):
        self.change_sprite(self.illu, self.current_illu())
        self.illu = self.current_illu()

        if self.character.intention is not None:
            inten = self.inten[self.character.intention]
            if inten is not self.intention_shown:
                # 用 change_sprite 替换，避免每帧往布局表里塞新条目
                if self.intention_shown is None:
                    self.add_sprite(inten, 0, 200, list_name="intention")
                else:
                    self.change_sprite(self.intention_shown, inten, "intention")
                self.intention_shown = inten
        elif self.intention_shown is not None:
            self.delete_sprite(self.intention_shown, "intention")
            self.intention_shown = None
