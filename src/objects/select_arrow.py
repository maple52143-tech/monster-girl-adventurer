import numpy as np
import math
import arcade
import pyglet

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
        self.arrow: list[pyglet.shapes.Circle] = []
        self.batch = batch
        min_radius = 5
        max_radius = 5
        num = 15
        for i in range(num):
            self.arrow.append(pyglet.shapes.Circle(0, 0, min_radius + max_radius / num * (i + 1),
                                                   color=(111, 111, 111), batch=self.batch))
        self.max_rad = max_radius + 20
        self.tri = pyglet.shapes.Triangle(0, 0, -(3 ** 0.5) * self.max_rad, self.max_rad, -(3 ** 0.5) * self.max_rad, -self.max_rad,
                                          color=(111, 111, 111), batch=self.batch)
        self.num = num + 1



    def update(self, x, y):
        if self.deck.selected is not None:
            self.visible = True
            x1, y1 = self.deck.selected.center_x, self.deck.selected.center_y
            x2, y2 = x, y
            self.a, self.b, self.c = quadratic_through_points(x1, y1, x2, y2, 20)

            for i in range(self.num - 1):
                ix = (x2 - x1) / self.num * i + x1
                iy = self.a * ix ** 2 + self.b * ix + self.c
                self.arrow[i].position = (ix, iy)

            angle = -np.arctan((y - self.arrow[-1].y) / (x - self.arrow[-1].x)) / np.pi * 180
            self.tri.position = (x, y)
            self.tri.rotation = angle if angle > 0 else 180 + angle
        else:
            self.visible = False


    def draw(self):
        if self.visible:
            self.batch.draw()