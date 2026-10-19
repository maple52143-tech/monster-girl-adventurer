"""arcade 版 UI 组件库（移植自旧 pygame 项目的 Object / StandardButton / Roulette 等）。

约定：
* 位置用归一化坐标（0~1 屏幕比例），内部换算成像素；坐标以控件中心为基准。
* 中文文本用 PIL + 项目自带 ttf 渲染成纹理再交给 arcade 画
  （该字体没有可用的家族名，无法用 ``font_name`` 走 pyglet 的字体查找）。
"""

from __future__ import annotations

from functools import lru_cache
from typing import Callable, Iterable, Sequence

import arcade
from PIL import Image, ImageDraw, ImageFont

from src.core.audio import audio
from src.core.settings import ASSETS, FONT_FILE, SCREEN_HEIGHT, SCREEN_WIDTH

# ---------------------------------------------------------------- 文本

WHITE = (255, 255, 255, 255)
DARK = (48, 36, 28, 255)


def _color(value) -> arcade.types.Color:
    """arcade 的 draw_texture_rect 只接受 Color 对象，这里统一转换。"""
    if isinstance(value, arcade.types.Color):
        return value
    return arcade.types.Color.from_iterable(value)


@lru_cache(maxsize=8)
def _pil_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_FILE), size)


def _wrap(text: str, font: ImageFont.FreeTypeFont, width: float | None) -> list[str]:
    if not width:
        return text.split("\n")
    lines: list[str] = []
    for raw in text.split("\n"):
        line = ""
        for ch in raw:
            if font.getlength(line + ch) <= width:
                line += ch
            else:
                lines.append(line)
                line = ch
        lines.append(line)
    return lines


@lru_cache(maxsize=1024)
def text_texture(text: str, size: int, color: tuple, width: int | None = None) -> arcade.Texture:
    """把一段文本渲染成纹理（支持换行与按像素宽度折行）。"""
    font = _pil_font(size)
    lines = _wrap(text, font, width)
    line_h = int(size * 1.35)
    text_w = max((font.getlength(line) for line in lines), default=1)
    img_w = int(text_w) + 10
    img_h = line_h * max(1, len(lines)) + 8
    img = Image.new("RGBA", (max(img_w, 1), max(img_h, 1)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        draw.text((5, 4 + line_h * i + line_h / 2), line, font=font,
                  fill=color, anchor="lm")
    return arcade.Texture(image=img)


def draw_text(text: str, x: float, y: float, size: int = 28, color: tuple = WHITE,
              anchor_x: str = "center", anchor_y: str = "center",
              width: int | None = None, shadow: bool = False) -> None:
    if not text:
        return
    if shadow:
        # 描边/阴影：同一段文字往右下偏移画一遍深色，提升浅底可读性
        draw_text(text, x + 2, y - 2, size, (20, 16, 14, min(200, color[3])),
                  anchor_x, anchor_y, width)
    tex = text_texture(text, size, tuple(color), width)
    w, h = tex.size
    dx = {"left": w / 2, "right": -w / 2}.get(anchor_x, 0.0)
    dy = {"top": -h / 2, "bottom": h / 2}.get(anchor_y, 0.0)
    arcade.draw_texture_rect(tex, arcade.XYWH(x + dx, y + dy, w, h))


def to_px(pos: Sequence[float]) -> tuple[float, float]:
    return pos[0] * SCREEN_WIDTH, pos[1] * SCREEN_HEIGHT


@lru_cache(maxsize=256)
def texture(path: str) -> arcade.Texture:
    return arcade.load_texture(str(path))


def img_path(*parts: str) -> str:
    return str(ASSETS.joinpath(*parts))


def fit_picture(pos: Sequence[float], path: str,
                box: tuple[float, float]) -> "Picture":
    """按比例把图片放进给定方框（保持长宽比）。"""
    t = texture(path)
    scale = min(box[0] / t.width, box[1] / t.height)
    return Picture(pos, path, size=(t.width * scale, t.height * scale))


# ---------------------------------------------------------------- 控件基类

class Widget:
    def __init__(self, pos: Sequence[float] = (0.5, 0.5)):
        self.x, self.y = to_px(pos)
        self.visible = True
        self.enabled = True
        # 是否参与鼠标事件分发（纯装饰的图片/文字应为 False）
        self.interactive = False

    def update(self, delta_time: float) -> None:
        pass

    def draw(self) -> None:
        pass

    def on_mouse_motion(self, x: float, y: float) -> None:
        pass

    def on_mouse_press(self, x: float, y: float, button: int) -> bool:
        return False

    def on_mouse_release(self, x: float, y: float, button: int) -> bool:
        return False

    @property
    def size(self) -> tuple[float, float]:
        return (0.0, 0.0)

    def contains(self, x: float, y: float) -> bool:
        w, h = self.size
        return (self.visible and self.enabled
                and abs(x - self.x) <= w / 2 and abs(y - self.y) <= h / 2)

    def hit_test(self, x: float, y: float) -> bool:
        """命中测试：决定这一次点击归哪个控件（避免下层控件被同时触发）。"""
        return self.interactive and self.contains(x, y)


# ---------------------------------------------------------------- 图片

class Picture(Widget):
    def __init__(self, pos: Sequence[float], path: str, scale: float = 1.0,
                 size: tuple[float, float] | None = None):
        super().__init__(pos)
        self.tex = texture(path)
        self.scale = scale
        self.fixed_size = size

    @property
    def size(self) -> tuple[float, float]:
        if self.fixed_size:
            return self.fixed_size
        return self.tex.width * self.scale, self.tex.height * self.scale

    def draw(self) -> None:
        if not self.visible:
            return
        w, h = self.size
        arcade.draw_texture_rect(self.tex, arcade.XYWH(self.x, self.y, w, h))


# ---------------------------------------------------------------- 文字

class TextLabel(Widget):
    def __init__(self, pos: Sequence[float], text: str, size: int = 32,
                 color: tuple = WHITE, anchor_y: str = "center", width: int | None = None):
        super().__init__(pos)
        self.text = text
        self.font_size = size
        self.color = color
        self.anchor_y = anchor_y
        self.width = width

    def draw(self) -> None:
        if self.visible:
            draw_text(self.text, self.x, self.y, self.font_size, self.color,
                      anchor_y=self.anchor_y, width=self.width)


# ---------------------------------------------------------------- 按钮

class Button(Widget):
    """图片按钮：悬停放大、按下、点击回调。"""

    def __init__(self, pos: Sequence[float], path: str | None = None,
                 label: str | None = None, size: tuple[float, float] | None = None,
                 scale: float = 1.0, font_size: int = 27,
                 on_click: Callable[[], None] | None = None,
                 label_offset: tuple[float, float] = (0.0, 0.0),
                 hover_zoom: float = 1.06, tint: tuple = WHITE,
                 label_color: tuple = WHITE):
        super().__init__(pos)
        self.tex = texture(path) if path else None
        self.scale = scale
        self.fixed_size = size
        self.label = label
        self.font_size = font_size
        self.label_offset = label_offset
        self.on_click = on_click
        self.hover_zoom = hover_zoom
        self.tint = tint
        self.label_color = label_color
        self.hovered = False
        self._hovered_last = False
        self._armed = False
        self._zoom = 1.0
        self.interactive = True

    @property
    def size(self) -> tuple[float, float]:
        if self.fixed_size:
            return self.fixed_size
        if self.tex is not None:
            return self.tex.width * self.scale, self.tex.height * self.scale
        return (0.0, 0.0)

    def update(self, delta_time: float) -> None:
        target = self.hover_zoom if (self.hovered and self.enabled) else 1.0
        self._zoom += (target - self._zoom) * min(1.0, delta_time * 14.0)

    def draw(self) -> None:
        if not self.visible:
            return
        w, h = self.size
        if self.tex is not None:
            arcade.draw_texture_rect(self.tex, arcade.XYWH(self.x, self.y, w, h),
                                     color=_color(self.tint))
        if self.label:
            draw_text(self.label, self.x + self.label_offset[0],
                      self.y + self.label_offset[1], self.font_size, self.label_color)

    def on_mouse_motion(self, x: float, y: float) -> None:
        self.hovered = self.contains(x, y)
        if self.hovered and not self._hovered_last:
            audio.touch()
        self._hovered_last = self.hovered

    def on_mouse_press(self, x: float, y: float, button: int) -> bool:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self._armed = self.contains(x, y)
        return False

    def on_mouse_release(self, x: float, y: float, button: int) -> bool:
        if button != arcade.MOUSE_BUTTON_LEFT or not self._armed:
            return False
        self._armed = False
        if not self.contains(x, y):
            return False
        audio.press()
        if self.on_click:
            self.on_click()
        return True


class IconButton(Button):
    """只有图标的按钮（状态图标 / 左右箭头）。"""

    def __init__(self, pos: Sequence[float], path: str, scale: float = 0.15, **kwargs):
        kwargs.setdefault("hover_zoom", 1.15)
        super().__init__(pos, path, scale=scale, **kwargs)


# ---------------------------------------------------------------- 卡片

class SlotCard(Widget):
    """存档位 / 角色位卡片：底板 + 标题 + 副标题（可带小头像）。"""

    BG = (232, 225, 208, 235)
    BG_HOVER = (250, 243, 224, 245)
    BORDER = (120, 96, 72, 255)

    def __init__(self, pos: Sequence[float], size: tuple[float, float],
                 title: str = "", subtitle: str = "",
                 on_click: Callable[[], None] | None = None,
                 empty: bool = False, icon: str | None = None,
                 title_size: int = 30, subtitle_size: int = 21,
                 bg: str | None = None, title_color: tuple = DARK,
                 subtitle_color: tuple = (110, 92, 74, 255)):
        super().__init__(pos)
        self._size = size
        self.title = title
        self.subtitle = subtitle
        self.on_click = on_click
        self.empty = empty
        self.title_size = title_size
        self.subtitle_size = subtitle_size
        self.icon = texture(icon) if icon else None
        # 用整张素材当底板（存档卡）时为 None，否则画纯色底板
        self.bg = texture(bg) if bg else None
        self.title_color = title_color
        self.subtitle_color = subtitle_color
        self.hovered = False
        self._hovered_last = False
        self._armed = False
        self._zoom = 1.0
        self.interactive = True

    @property
    def size(self) -> tuple[float, float]:
        return self._size

    def update(self, delta_time: float) -> None:
        target = 1.04 if (self.hovered and self.enabled) else 1.0
        self._zoom += (target - self._zoom) * min(1.0, delta_time * 14.0)

    def draw(self) -> None:
        if not self.visible:
            return
        w, h = self._size[0] * self._zoom, self._size[1] * self._zoom
        rect = arcade.XYWH(self.x, self.y, w, h)
        if self.bg is not None:
            # 卡片素材是「相框」：内部是透明的，先垫一层纸色再画框
            paper = arcade.XYWH(self.x, self.y, w * 0.86, h * 0.9)
            arcade.draw_rect_filled(paper, (236, 228, 210, 255))
            arcade.draw_texture_rect(self.bg, rect)
        else:
            arcade.draw_rect_filled(rect, self.BG_HOVER if self.hovered else self.BG)
            arcade.draw_rect_outline(rect, self.BORDER, 3)
        text_center_y = self.y + h * 0.16
        if self.icon is not None:
            ih = min(h * 0.45, self.icon.height)
            iw = self.icon.width * (ih / self.icon.height)
            arcade.draw_texture_rect(self.icon, arcade.XYWH(self.x, self.y + h * 0.16, iw, ih))
            text_center_y = self.y - h * 0.18
        if self.title:
            draw_text(self.title, self.x, text_center_y, self.title_size,
                      self.title_color, width=int(w * 0.9))
        if self.subtitle:
            draw_text(self.subtitle, self.x, self.y - h * 0.34, self.subtitle_size,
                      self.subtitle_color, width=int(w * 0.9))

    def on_mouse_motion(self, x: float, y: float) -> None:
        self.hovered = self.contains(x, y)
        if self.hovered and not self._hovered_last:
            audio.touch()
        self._hovered_last = self.hovered

    def on_mouse_press(self, x: float, y: float, button: int) -> bool:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self._armed = self.contains(x, y)
        return False

    def on_mouse_release(self, x: float, y: float, button: int) -> bool:
        if button != arcade.MOUSE_BUTTON_LEFT or not self._armed:
            return False
        self._armed = False
        if not self.contains(x, y):
            return False
        audio.press()
        if self.on_click:
            self.on_click()
        return True


# ---------------------------------------------------------------- 轮盘

class Roulette(Widget):
    """水平轮盘：中间为当前项，两侧依次缩小后退，切换带缓动。"""

    def __init__(self, pos: Sequence[float], items: list[Widget],
                 spacing: float = 420.0, max_show: int = 3, zoom_factor: float = 0.8):
        super().__init__(pos)
        self.items = items
        self.spacing = spacing
        self.max_show = max_show
        self.zoom_factor = zoom_factor
        self.pointer = 0
        self._offsets = [float(i * spacing) for i in range(len(items))]
        self._z = [1.0] * len(items)
        self.interactive = True

    def hit_test(self, x: float, y: float) -> bool:
        """只有点在自己可见的卡片上才算命中，避免吞掉其它按钮的点击。"""
        if not (self.visible and self.enabled):
            return False
        return any(item.hit_test(x, y) for item in self.items if item.visible)

    def update(self, delta_time: float) -> None:
        k = min(1.0, delta_time * 10.0)
        half = self.max_show // 2
        for i, item in enumerate(self.items):
            target = (i - self.pointer) * self.spacing
            self._offsets[i] += (target - self._offsets[i]) * k
            dist = abs(i - self.pointer)
            target_z = self.zoom_factor ** dist
            self._z[i] += (target_z - self._z[i]) * k
            item.x = self.x + self._offsets[i]
            item.y = self.y
            # 只显示 max_show 个（居中 + 两侧各 half 个）
            item.visible = self.visible and dist <= max(0, half)
            if isinstance(item, SlotCard):
                item._zoom = self._z[i] * (1.04 if item.hovered else 1.0)
            item.update(delta_time)

    def draw(self) -> None:
        order = sorted(range(len(self.items)), key=lambda i: -abs(i - self.pointer))
        for i in order:
            self.items[i].draw()

    def on_mouse_motion(self, x: float, y: float) -> None:
        for item in self.items:
            item.on_mouse_motion(x, y)

    def on_mouse_press(self, x: float, y: float, button: int) -> bool:
        # 只把「按下」传给真正被点到的卡片，其余卡片不会被 arm
        for item in self.items:
            if item.visible and item.hit_test(x, y):
                item.on_mouse_press(x, y, button)
        return True

    def on_mouse_release(self, x: float, y: float, button: int) -> bool:
        for i, item in enumerate(self.items):
            if item.on_mouse_release(x, y, button):
                self.pointer = i
                return True
        return False

    def on_mouse_scroll(self, x: float, y: float, scroll_y: float) -> bool:
        if scroll_y > 0:
            self.left()
        elif scroll_y < 0:
            self.right()
        return True

    def left(self) -> None:
        if self.pointer > 0:
            self.pointer -= 1

    def right(self) -> None:
        if self.pointer < len(self.items) - 1:
            self.pointer += 1

    @property
    def can_left(self) -> bool:
        return self.pointer > 0

    @property
    def can_right(self) -> bool:
        return self.pointer < len(self.items) - 1

    @property
    def current(self) -> Widget | None:
        return self.items[self.pointer] if 0 <= self.pointer < len(self.items) else None


# ---------------------------------------------------------------- 背景

class ZoomSlideshow:
    """缓慢放大并轮换的背景（对应旧项目 BackgroundObject(is_slide=True)）。"""

    def __init__(self, paths: Iterable[str], max_zoom: float = 1.35, speed: float = 0.06):
        self.textures = [texture(p) for p in paths]
        self.max_zoom = max_zoom
        self.speed = speed
        self.index = 0
        self.zoom = 1.0
        self.offset = (0.0, 0.0)

    def update(self, delta_time: float, mouse_x: float, mouse_y: float) -> None:
        self.zoom += self.speed * delta_time
        if self.zoom > self.max_zoom and self.textures:
            self.zoom = 1.0
            self.index = (self.index + 1) % len(self.textures)
        tx = -(mouse_x / SCREEN_WIDTH - 0.5) * 40
        ty = (mouse_y / SCREEN_HEIGHT - 0.5) * 24
        self.offset = (self.offset[0] + (tx - self.offset[0]) * min(1, delta_time * 3),
                       self.offset[1] + (ty - self.offset[1]) * min(1, delta_time * 3))

    def draw(self) -> None:
        if not self.textures:
            return
        t = self.textures[self.index]
        cover = max(SCREEN_WIDTH / t.width, SCREEN_HEIGHT / t.height)
        scale = cover * self.zoom
        arcade.draw_texture_rect(
            t, arcade.XYWH(SCREEN_WIDTH / 2 + self.offset[0],
                           SCREEN_HEIGHT / 2 + self.offset[1],
                           t.width * scale, t.height * scale))


# ---------------------------------------------------------------- 消息框

class MessageBox(Widget):
    """模态确认框：文字 + 确定/取消。"""

    def __init__(self):
        super().__init__((0.5, 0.5))
        self.visible = False
        self.message = ""
        self.callback: Callable[[bool], None] | None = None
        bg = img_path("images", "ui", "simple_button_bg.png")
        self._ok = Button((0.445, 0.40), bg, "确定", size=(190, 76), font_size=28,
                          on_click=lambda: self.close(True))
        self._cancel = Button((0.555, 0.40), bg, "取消", size=(190, 76), font_size=28,
                              on_click=lambda: self.close(False))

    def ask(self, message: str, callback: Callable[[bool], None]) -> None:
        self.message = message
        self.callback = callback
        self.visible = True

    def close(self, result: bool) -> None:
        if not self.visible:
            return
        self.visible = False
        cb, self.callback = self.callback, None
        if cb:
            cb(result)

    def update(self, delta_time: float) -> None:
        self._ok.update(delta_time)
        self._cancel.update(delta_time)

    def draw(self) -> None:
        if not self.visible:
            return
        arcade.draw_rect_filled(
            arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT),
            (0, 0, 0, 150))
        panel = arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 760, 280)
        arcade.draw_rect_filled(panel, (245, 238, 224, 250))
        arcade.draw_rect_outline(panel, (120, 96, 72, 255), 4)
        draw_text(self.message, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 52, 30, DARK,
                  width=660)
        self._ok.draw()
        self._cancel.draw()

    def on_mouse_motion(self, x: float, y: float) -> None:
        if self.visible:
            self._ok.on_mouse_motion(x, y)
            self._cancel.on_mouse_motion(x, y)

    def on_mouse_press(self, x: float, y: float, button: int) -> bool:
        if not self.visible:
            return False
        self._ok.on_mouse_press(x, y, button)
        self._cancel.on_mouse_press(x, y, button)
        return True

    def on_mouse_release(self, x: float, y: float, button: int) -> bool:
        if not self.visible:
            return False
        self._ok.on_mouse_release(x, y, button)
        self._cancel.on_mouse_release(x, y, button)
        return True


# ---------------------------------------------------------------- 提示框

class HintBox(Widget):
    """底部提示条。"""

    def __init__(self):
        super().__init__((0.5, 0.032))
        self.visible = False
        self.text = ""
        self.alpha = 0.0

    def show(self, text: str) -> None:
        if text:
            self.text = text
            self.visible = True

    def hide(self) -> None:
        self.visible = False

    def update(self, delta_time: float) -> None:
        target = 1.0 if self.visible else 0.0
        self.alpha += (target - self.alpha) * min(1.0, delta_time * 10.0)

    def draw(self) -> None:
        if self.alpha <= 0.02 or not self.text:
            return
        a = int(self.alpha * 235)
        w = min(SCREEN_WIDTH - 160, 80 + len(self.text) * 28)
        panel = arcade.XYWH(SCREEN_WIDTH / 2, self.y, w, 62)
        arcade.draw_rect_filled(panel, (20, 18, 16, a))
        arcade.draw_rect_outline(panel, (232, 205, 160, a), 2)
        draw_text(self.text, SCREEN_WIDTH / 2, self.y, 24, (240, 232, 220, a),
                  width=int(w - 40))
