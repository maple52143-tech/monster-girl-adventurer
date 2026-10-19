import arcade

from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.tools.timer import Timer

class Plot:
    def __init__(self, sprite: arcade.Sprite, timer: Timer, mode: str = "follow"):
        self.sprite = sprite
        self.timer = timer
        self.mode = mode

class PlotManager:
    def __init__(self):
        self._show = []
        self.delegate: list[Plot] = []

    @property
    def show(self):
        return self._show

    def title(self, text: str, time: float = 1.5):
        t = arcade.Text(text, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                        arcade.csscolor.WHITE, 60, anchor_x='center', anchor_y='baseline')
        self.delegate.append(Plot(t, Timer(time), mode="follow"))

    def update(self, delta_time: float):
        for d in tuple(self.delegate):
            if d.timer.update(delta_time):
                self.delegate.remove(d)

        # 按顺序展出：遇到第一条 follow 提示就独占屏幕，meantime 的与它并行
        self._show = []
        for d in self.delegate:
            self._show.append(d.sprite)
            if d.mode == "follow":
                break

plot_manager = PlotManager()