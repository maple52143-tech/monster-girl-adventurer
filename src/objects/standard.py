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

        self.parts: list[list[arcade.Sprite | float]] = []
        self.is_moving = True
        self.flip = [False, False]

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

    def add_sprite(self, sprite: arcade.Sprite, x: float, y: float, angle: float = 0, list_name = "default"):
        self.parts.append([sprite, x, y, angle])
        self.sprites.add_sprite(list_name, sprite)

    def delete_sprite(self, sprite: arcade.Sprite, list_name = "default"):
        self.sprites[list_name].remove(sprite)
        self.parts.pop(self._find_sprite(sprite))

    def change_sprite(self, old_sprite: arcade.Sprite, new_sprite: arcade.Sprite, list_name = "default"):
        self.sprites[list_name].remove(old_sprite)
        self.sprites.add_sprite(list_name, new_sprite)
        self.parts[self._find_sprite(old_sprite)][0] = new_sprite
        self.update_position()

    def _find_sprite(self, sprite: arcade.Sprite):
        for i, s in enumerate(self.parts):
            if sprite in s:
                return i
        return None

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

        for s in self.parts:
            sx = s[1]
            sy = s[2]
            s[0].scale = (s[0].scale[0] * (-1 if self.flip[0] and s[0].scale[0] > 0 else 1), s[0].scale[1] * (-1 if self.flip[1] and s[0].scale[1] > 0 else 1))
            if self.flip[0]:
                sx = self.size[0] - sx
            if self.flip[1]:
                sy = self.size[1] - sy
            s[0].center_x = sx + self._x + dx
            s[0].center_y = sy + self._y + dy
            s[0].angle = s[3]

    def draw(self):
        if self.is_moving:
            self.update_position()
            self.is_moving = False

        self.sprites.draw()
