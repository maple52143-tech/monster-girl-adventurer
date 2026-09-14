import numpy as np
import math
import arcade
import pyglet

from src.core.settings import SCREEN_WIDTH
from src.objects.standard import StandardSet
from src.objects.deck import Deck

def quadratic_through_points(x1, y1, x2, y2, d):
    """
    求过两点 (x1, y1) 和 (x2, y2) 的二次函数 f(x) = ax² + bx + c，
    其顶点（最高点）位于两点之间，且顶点纵坐标比 max(y1, y2) 高 d。
    返回 (a, b, c)，若无解则返回 None。
    """
    # 保证 x1 < x2
    if x1 > x2:
        x1, y1, x2, y2 = x2, y2, x1, y1
    elif x1 == x2:
        raise ValueError("两点横坐标必须不同")

    k = max(y1, y2) + d
    A = y1 - k
    B = y2 - k

    # 求解 h 的方程：(A-B) h^2 + 2*(B*x1 - A*x2) h + (A*x2^2 - B*x1^2) = 0
    coeff_a = A - B
    coeff_b = 2 * (B * x1 - A * x2)
    coeff_c = A * x2**2 - B * x1**2

    # 解二次方程
    if abs(coeff_a) < 1e-12:  # 退化为一次方程
        if abs(coeff_b) < 1e-12:
            return None
        h = -coeff_c / coeff_b
    else:
        disc = coeff_b**2 - 4 * coeff_a * coeff_c
        if disc < 0:
            return None
        sqrt_disc = math.sqrt(disc)
        h1 = (-coeff_b + sqrt_disc) / (2 * coeff_a)
        h2 = (-coeff_b - sqrt_disc) / (2 * coeff_a)
        # 选择在 (x1, x2) 内的根
        candidates = [h for h in (h1, h2) if x1 < h < x2]
        if not candidates:
            return None
        # 若有多个，选择靠近区间中心的
        h = min(candidates, key=lambda h: abs(h - (x1 + x2) / 2))

    # 计算 a
    if abs(x1 - h) < 1e-12:  # 顶点与端点重合，不符合要求
        return None
    a = (y1 - k) / ((x1 - h) ** 2)

    # 检查开口方向
    if a >= 0:
        return None

    # 转换为标准系数
    b = -2 * a * h
    c = a * h * h + k

    # 可选：验证通过两点
    # assert abs(a*x1*x1 + b*x1 + c - y1) < 1e-12
    # assert abs(a*x2*x2 + b*x2 + c - y2) < 1e-12

    return a, b, c



class SelectArrow:
    def __init__(self, deck: Deck, batch: pyglet.graphics.Batch):
        self.visible = False
        self.deck = deck
        self.a = -5 * 10 ** -2
        self.b = 0
        self.c = 0
        self.arrow: dict[str, list[pyglet.shapes.Circle]] = {}
        self.batch = batch
        min_radius = 5
        max_radius = 5
        num = 15

        self.max_rad = max_radius + 20
        self.tri: dict[str, pyglet.shapes.Triangle] = {}

        def new_arrow(color:tuple[int, int, int] = (255, 255, 255), name: str = "normal"):
            if name not in self.arrow:
                self.arrow[name] = []

            for i in range(num):
                self.arrow[name].append(pyglet.shapes.Circle(0, 0, min_radius + max_radius / num * (i + 1),
                                                       color= color, batch=self.batch))
            self.tri[name] = pyglet.shapes.Triangle(0, 0, -(3 ** 0.5) * self.max_rad, self.max_rad, -(3 ** 0.5) * self.max_rad,
                                   -self.max_rad,
                                   color=color, batch=self.batch)

        new_arrow((111, 111, 111), 'normal')
        new_arrow((255, 108, 63), 'enemy')
        new_arrow((96, 228, 255), 'team')

        self.num = num + 1
        self.show_type = 'normal'


    def update(self, x, y):

        if self.deck.selected is not None:
            self.visible = True
            x1, y1 = self.deck.selected.center_x, self.deck.selected.center_y
            x2, y2 = x, y
            self.a, self.b, self.c = quadratic_through_points(x1, y1, x2, y2, 20)

            for i in range(self.num - 1):
                ix = (x2 - x1) / self.num * i + x1
                iy = self.a * ix ** 2 + self.b * ix + self.c
                for name in self.arrow.keys():
                    self.arrow[name][i].position = (ix, iy)

            for name, tri in self.tri.items():
                last = self.arrow[name][-1]
                dx, dy = x - last.x, y - last.y
                length = math.hypot(dx, dy)
                if length < 1e-6:
                    continue
                ux, uy = dx / length, dy / length
                px, py = -uy, ux  # 垂直方向

                R = self.max_rad
                H = math.sqrt(3) * R
                bcx, bcy = x - ux * H, y - uy * H

                tri.x, tri.y = x, y
                tri.x2, tri.y2 = bcx + px * R, bcy + py * R
                tri.x3, tri.y3 = bcx - px * R, bcy - py * R
        else:
            self.visible = False

        self.show_type = 'normal'
        if self.visible:
            match self.deck.selected.type:
                case "attack":
                    if x >= SCREEN_WIDTH / 2:
                        self.show_type = 'enemy'
                case "skill":
                    if x < SCREEN_WIDTH / 2:
                        self.show_type = 'team'

            for name in self.arrow.keys():
                if name != self.show_type:
                    for shape in self.arrow[name]:
                        shape.batch = None
                    self.tri[name].batch = None
                else:
                    for shape in self.arrow[name]:
                        shape.batch = self.batch
                    self.tri[name].batch = self.batch

    def draw(self):
        pass