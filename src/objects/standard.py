import arcade


class StandardSet:
    def __init__(self, x, y, anchor_x: str, anchor_y: str, size: tuple[float, float]):
        self.sprites = arcade.SpriteList()
        self.x = x
        self.y = y
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.size = size

        self.parts: list[list[arcade.Sprite | float]] = []
        self.is_moving = True

    def add_sprite(self, sprite: arcade.Sprite, x: float, y: float, angle: float = 0):
        self.parts.append([sprite, x, y, angle])
        self.sprites.append(sprite)

    def delete_sprite(self, sprite: arcade.Sprite):
        self.sprites.remove(sprite)
        self.parts.pop(self._find_sprite(sprite))

    def change_sprite(self, old_sprite: arcade.Sprite, new_sprite: arcade.Sprite):
        self.sprites.remove(old_sprite)
        self.sprites.append(new_sprite)
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
            s[0].center_x = s[1] + self.x + dx
            s[0].center_y = s[2] + self.y + dy
            s[0].angle = s[3]

    def draw(self):
        if self.is_moving:
            self.update_position()
            self.is_moving = False

        self.sprites.draw()
