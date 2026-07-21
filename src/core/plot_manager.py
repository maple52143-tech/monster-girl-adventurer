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
        self._show = []
        for i, d in enumerate(self.delegate):
            if d.timer.update(delta_time):
                self.delegate.remove(d)
            else:
                self._show.append(d.sprite)
                if i < len(self.delegate) - 1:
                    match self.delegate[i + 1].mode:
                        case "follow":
                            break
                        case "meantime":
                            continue

plot_manager = PlotManager()