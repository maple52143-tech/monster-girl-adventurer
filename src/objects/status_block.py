import arcade

from src.objects.standard import StandardSet
from src.objects.character import Character
from src.core.resource_manager import res_manager
from src.tools.digit_renderer import DigitRenderer


class StatusBlock(StandardSet):
    """角色状态栏：头像 + 带心形标志的血条框 + 红条 + 数字。

    hp_bar.png 的构成（素材像素坐标，贴图总宽 1200）：
      * 心形标志在左边（约 x 25..182）——血量数字放在这里
      * 血条内腔 x 184..1052、y 105..153 —— 红条铺在这里
    贴图本身是“头像在左、血条在右”画的，所以：
      * 我方（avatar_on_left=True）：原样使用，红条从内腔左沿向右铺
      * 敌方：整块镜像（头像与心形到右边），红条表现为从右沿向左铺
    """

    BAR_INNER_LEFT_PX = 184
    BAR_INNER_RIGHT_PX = 1052
    BAR_INNER_TOP_PX = 90
    BAR_INNER_BOTTOM_PX = 160
    # 心形标志中心（放血量数字的位置；单位与上面一致，相对 hp_bar 贴图左沿）
    HEART_CENTER_PX = 70
    # 敌方专用：整块镜像后数字不一定是镜像对称的，用这个单独微调（None = 直接镜像）
    ENEMY_HEART_CENTER_PX = 1030
    # 护盾数字相对心形（血量数字）的偏移；MP 数字的位置
    SHIELD_OFFSET_PX = 480
    MP_CENTER_PX = 1180
    # 红条锚定端的额外微调（单位同上，正值 = 朝内收）。
    # 两边都是“心形那一端”对齐内腔，若视觉上还想再挪，改这两个值即可。
    BAR_INSET_PX = 0
    ENEMY_BAR_INSET_PX = 30

    def __init__(self, x: float, y: float, character: Character, avatar_on_left: bool = True):
        avatar_size = 84
        hp_bar_size = 0.23
        self.avatar_on_left = avatar_on_left
        super().__init__(x, y, "left", "top", (264, avatar_size))
        # 敌方整块镜像：头像与心形跑到右边，红条随之从右侧减少
        self.flip = [not avatar_on_left, False]

        self.avatar = arcade.Sprite(character.avatar, scale=0.07)
        self.add_sprite(self.avatar, self.avatar.width / 2, self.avatar.height / 2)

        self.select = arcade.Sprite(res_manager.image("choose_corner"), 0.1)
        self.add_sprite(self.select, self.select.width / 2, self.size[1] - self.select.height / 2)

        self.hp_bar = arcade.Sprite(res_manager.image("hp_bar"), hp_bar_size)
        self.hp_bar_shield = arcade.Sprite(res_manager.image("hp_bar_shield"), hp_bar_size)
        self.add_sprite(self.hp_bar, avatar_size + self.hp_bar.width / 2, self.size[1] / 2)
        self.add_sprite(self.hp_bar_shield, avatar_size + self.hp_bar.width / 2, self.size[1] / 2)
        self.sprites.add_sprite_list_before("bar", "default")

        self.hp_bar_size = hp_bar_size
        self.avatar_size = avatar_size
        # 红条满血宽度 = 内腔宽度；高度 = 内腔高度
        self.bar_full_width = (self.BAR_INNER_RIGHT_PX - self.BAR_INNER_LEFT_PX) * hp_bar_size
        self.bar_bottom = self.size[1] - self.hp_bar.height + self.BAR_INNER_TOP_PX * hp_bar_size
        self.bar = arcade.SpriteSolidColor(int(self.bar_full_width),
                                           int((self.BAR_INNER_BOTTOM_PX - self.BAR_INNER_TOP_PX) * hp_bar_size),
                                           color=arcade.csscolor.RED)
        # 血条尺寸由血量决定，不能参与布局的镜像缩放（否则宽度会被满血值覆盖）
        self.set_sprite_scale_locked(self.bar)
        self.add_sprite(self.bar, self.bar_full_width / 2,
                        self.bar_bottom + self.bar.height / 2, 0, "bar")

        self.character = character
        self.is_chosen = True
        # 内腔可视位置的缓存与标定时的块坐标（块移动后会重标）
        self._inner_visual_left = 0.0
        self._inner_visual_right = 0.0
        self._calibrated_x = None
        self._calibrated_y = None
        self._calibrate_bar()

        self.mp_text = DigitRenderer('_mp', 0.025, align='left')
        self.shield_text = DigitRenderer('_mp', 0.025, align='left')
        self.hp_text = DigitRenderer('_hp', 0.025, align='left')

    # ------------------------------------------------------------ 血条定位

    def _visual_left(self, sprite) -> float:
        w = sprite.width
        return min(sprite.center_x + w / 2, sprite.center_x - w / 2)

    def _calibrate_bar(self):
        """量出内腔的可视左右沿，并记住当前块位置。

        只用 hp_bar 布局后的真实坐标 + 素材像素范围换算，不再手推块局部坐标；
        块位置变化时要重新标定（CombatShow 是在构造之后才设置 x/y 的）。
        """
        self.update_position()
        self._inner_visual_left = self._visual_left(self.hp_bar) + \
            self.BAR_INNER_LEFT_PX * self.hp_bar_size
        self._inner_visual_right = self._inner_visual_left + self.bar_full_width
        self._calibrated_x = self._x
        self._calibrated_y = self._y

    def set_bar(self, ratio: float):
        """按血量比例设置红条：锚定在“心形同侧”的内腔那一端。

        红条从内腔的“心形那一端”开始缩短：
          * 我方（心形在左）：贴住内腔左沿，掉血时向右缩
          * 敌方（整块镜像、心形在右）：贴住内腔右沿，掉血时向左缩

        布局里 ``center_x = entry + 块x``，可视左沿 = center_x - 宽度/2；
        镜像时可视坐标被 ``size[0]`` 反射。
        """
        if self.x != self._calibrated_x or self.y != self._calibrated_y:
            self._calibrate_bar()

        ratio = max(0.0, min(1.0, ratio))
        self.bar.width = self.bar_full_width * ratio
        width = self.bar.width
        if self.avatar_on_left:
            anchor = self._inner_visual_left + self.BAR_INSET_PX * self.hp_bar_size
            entry = anchor + width / 2 - self._x
        else:
            anchor = self._inner_visual_right - self.ENEMY_BAR_INSET_PX * self.hp_bar_size
            entry = self._x + self.size[0] - anchor + width / 2
        self._set_part_x(self.bar, entry)
        part = self.get_part(self.bar)
        if part is not None:
            part[2] = self.bar_bottom
        self.is_moving = True

    # ------------------------------------------------------------ 每帧

    def update(self):
        self.set_sprite_visible(self.hp_bar_shield, self.character.shield > 0)
        self.set_sprite_visible(self.select, self.is_chosen and self.character.alive)

        self.set_bar(self.character.hp / self.character.max_hp)

        # 数字位置。镜像时 sprite.width 为负，`center ± width/2` 里的“左”会翻转，
        # 所以不要用它，改用不依赖符号的写法：贴图左侧 = 可见区间的较小端。
        ty = self.hp_bar.center_y
        tex_left = self._visual_left(self.hp_bar)

        def at(art_px: float) -> float:
            """把“素材 x”换算成屏幕坐标（贴图始终从左往右排，与镜像无关）。"""
            return tex_left + art_px * self.hp_bar_size

        heart_px = self.HEART_CENTER_PX
        if self.ENEMY_HEART_CENTER_PX is not None and not self.avatar_on_left:
            heart_px = self.ENEMY_HEART_CENTER_PX
        self.hp_text.position = (at(heart_px), ty)
        self.hp_text.digit = int(self.character.hp)
        self.shield_text.position = (at(heart_px + self.SHIELD_OFFSET_PX), ty)
        self.shield_text.digit = int(self.character.shield)
        self.mp_text.position = (at(self.MP_CENTER_PX), ty)
        self.mp_text.digit = int(self.character.mp)
        if self.character.type == 'character':
            self.mp_text.visible = True
            self.shield_text.visible = self.character.shield > 0
        else:
            self.mp_text.visible = False
            self.shield_text.visible = False
        self.is_moving = True

    def draw(self):
        super().draw()

        # 数字不是 sprite，需要手动跟随整体淡出
        self.mp_text.fade = self.fade
        self.shield_text.fade = self.fade
        self.hp_text.fade = self.fade

        self.mp_text.draw()
        self.shield_text.draw()
        self.hp_text.draw()
