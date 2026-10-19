import arcade


class StandardSet:
    def __init__(self, x, y, anchor_x: str, anchor_y: str, size: tuple[float, float]):
        self.sprites = arcade.Scene()
        self.sprites.add_sprite_list("default")
        self._x = x
        self._y = y
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.size = size

        # 按 sprite 索引，避免每帧重建时旧条目累积
        self.parts: dict[arcade.Sprite, list] = {}
        self.ori_scale: dict[arcade.Sprite, tuple[float, float]] = {}
        self.is_moving = True
        self.flip = [False, False]

        self.visible = True
        self._fade = 1.0
        # 记录过 visible=False 的 sprite：布局重算时只负责让它们保持隐藏，不去强行点亮
        self._hidden: set[arcade.Sprite] = set()
        # 自己管尺寸的 sprite（例如按血量伸缩的血条）：布局重算不碰它的 scale
        self._scale_locked: set[arcade.Sprite] = set()

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, value):
        self._x = value
        self.is_moving = True

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, value):
        self._y = value
        self.is_moving = True

    @property
    def fade(self):
        """0.0~1.0 的整体不透明度（用于死亡淡出）。"""
        return self._fade
    @fade.setter
    def fade(self, value):
        value = min(1.0, max(0.0, value))
        if value == self._fade:
            return
        self._fade = value
        self._apply_alpha()

    def _apply_alpha(self):
        alpha = int(round(self._fade * 255))
        for sprite_list in self.sprites._sprite_lists:
            sprite_list.alpha = alpha

    def add_sprite(self, sprite: arcade.Sprite, x: float, y: float, angle: float = 0, list_name = "default"):
        self.parts[sprite] = [sprite, x, y, angle]
        self.sprites.add_sprite(list_name, sprite)
        self.is_moving = True

    def delete_sprite(self, sprite: arcade.Sprite, list_name = "default"):
        self.sprites[list_name].remove(sprite)
        self.parts.pop(sprite, None)

    def change_sprite(self, old_sprite: arcade.Sprite, new_sprite: arcade.Sprite, list_name = "default"):
        self.sprites[list_name].remove(old_sprite)
        self.sprites.add_sprite(list_name, new_sprite)
        entry = self.parts.pop(old_sprite, None)
        if entry is not None:
            entry[0] = new_sprite
            self.parts[new_sprite] = entry
            self.ori_scale.pop(old_sprite, None)
        self.is_moving = True

    def clear_parts(self):
        """清空布局表（用于每帧重建的内容，例如手牌）。"""
        self.parts.clear()
        self.ori_scale.clear()
        self._hidden.clear()
        self._scale_locked.clear()

    def set_sprite_scale_locked(self, sprite: arcade.Sprite, locked: bool = True):
        """声明某个 sprite 自己管理 scale（不参与布局的对称/镜像缩放），但仍参与定位。"""
        if locked:
            self._scale_locked.add(sprite)
        else:
            self._scale_locked.discard(sprite)

    def set_sprite_visible(self, sprite: arcade.Sprite, value: bool):
        """设置单个 sprite 的可见性；StandardSet 只会在布局重算时保持它的隐藏状态。"""
        if value:
            self._hidden.discard(sprite)
        else:
            self._hidden.add(sprite)
        sprite.visible = value

    def get_part(self, sprite: arcade.Sprite):
        return self.parts.get(sprite)

    def _set_part_x(self, sprite: arcade.Sprite, value: float):
        """直接改写某个 sprite 的布局坐标（下次布局重算时生效）。"""
        entry = self.parts.get(sprite)
        if entry is not None:
            entry[1] = value

    def update_position(self):
        dx, dy = 0, 0
        match self.anchor_x:
            case "left": dx = 0
            case "right": dx = -self.size[0]
            case "center": dx = -self.size[0] / 2
        match self.anchor_y:
            case "top": dy = -self.size[1]
            case "bottom": dy = 0
            case "center": dy = -self.size[1] / 2

        for s in self.parts.values():
            sprite = s[0]
            # 镜像基于记录的原始缩放做绝对值处理，保证多次调用结果一致（不会正负来回翻）；
            # 自己管尺寸的 sprite（血条）跳过这一步，否则宽度会被覆盖
            if sprite not in self._scale_locked:
                ori = self.ori_scale.setdefault(sprite, tuple(sprite.scale))
                sx = ori[0] * (-1 if self.flip[0] else 1)
                sy = ori[1] * (-1 if self.flip[1] else 1)
                if tuple(sprite.scale) != (sx, sy):
                    sprite.scale = (sx, sy)

            px = s[1]
            py = s[2]
            if self.flip[0]:
                px = self.size[0] - px
            if self.flip[1]:
                py = self.size[1] - py
            sprite.center_x = px + self._x + dx
            sprite.center_y = py + self._y + dy
            sprite.angle = s[3]
            if sprite in self._hidden:
                sprite.visible = False

    def draw(self):
        if not self.visible or self._fade <= 0.0:
            return
        if self.is_moving:
            self.update_position()
            self.is_moving = False

        self.sprites.draw()
