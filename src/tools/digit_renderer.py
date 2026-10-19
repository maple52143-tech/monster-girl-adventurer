import arcade

from src.core.resource_manager import res_manager

class DigitRenderer:
    def __init__(self, category: str = '_normal', scale: float = 1.0, x: float = 0.0, y: float = 0.0, align: str = 'center'):
        self.textures: dict[str, arcade.Texture] = {}
        for d in "0123456789":
            tex = arcade.load_texture(res_manager.image(d + category))
            self.textures[d] = tex

        sample = next(iter(self.textures.values()))
        self.scale = scale
        self.digit_w = sample.width * scale
        self.digit_h = sample.height * scale

        self._digit = 0
        self._x = x
        self._y = y
        self._align = align
        self.spacing = 0.0
        self.visible = True
        self.fade = 1.0

    def get_width(self, value, spacing: float = 0.0) -> float:
        n = len(str(value))
        return n * self.digit_w + (n - 1) * spacing

    @property
    def digit(self):
        return self._digit
    @digit.setter
    def digit(self, value):
        self._digit = value
        return

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, value):
        self._y = value

    @property
    def align(self):
        return self._align
    @align.setter
    def align(self, value):
        self._align = value

    @property
    def position(self):
        return (self._x, self._y)
    @position.setter
    def position(self, value: tuple):
        self._x, self._y = value

    def draw(self):
        if self.visible:
            alpha = int(max(0.0, min(1.0, self.fade)) * 255)
            if alpha <= 0:
                return
            s = str(self._digit)
            total_w = self.get_width(self._digit, self.spacing)

            if self._align == "center":
                x = self._x - total_w / 2 + self.digit_w / 2
            elif self._align == "left":
                x = self._x + self.digit_w / 2
            else:
                x = self._x - total_w + self.digit_w / 2

            for ch in s:
                tex = self.textures.get(ch)
                if tex is None:      # 处理 '-' 等非数字字符
                    x += self.digit_w + self.spacing
                    continue
                arcade.draw_texture_rect(tex, arcade.XYWH(x, self._y, self.digit_w, self.digit_h), alpha=alpha)
                x += self.digit_w + self.spacing
        else:
            return