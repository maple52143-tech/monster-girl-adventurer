import arcade

from arcade.experimental.shadertoy import Shadertoy
from arcade.gl.framebuffer import Framebuffer

from src.core.resource_manager import res_manager
from src.core.game_window import GameWindow

class Shadertest(arcade.View):
    def __init__(self, window: GameWindow):
        super().__init__(window=window)
        self.enter_time = 0
        self.lighted = False
        # 实验性添加着色器渲染
        self.shadertoy: Shadertoy = None
        self.channel0: Framebuffer = None
        self.channel1: Framebuffer = None
        self.channel2: Framebuffer = None
        self.channel3: Framebuffer = None
        self.load_shader()
        self.time = 0
        self.delta_time = 0

    def load_shader(self):
        window_size = self.window.size

        self.shadertoy = Shadertoy(window_size, res_manager.shader("test_learning"))

        self.channel0 = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture(window_size, components=4)]
        )
        self.channel1 = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture(window_size, components=4)]
        )
        self.channel2 = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture(window_size, components=4)]
        )
        self.channel3 = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture(window_size, components=4)]
        )

        self.shadertoy.channel_0 = self.channel0.color_attachments[0]
        self.shadertoy.channel_1 = self.channel1.color_attachments[0]
        self.shadertoy.channel_2 = self.channel2.color_attachments[0]
        self.shadertoy.channel_3 = self.channel3.color_attachments[0]
        # noise = Shadertoy(window_size, res_manager.shader("rgba_noise"))
        # self.channel0.use()
        # self.channel0.clear()
        # noise.render()
        # self.channel1.use()
        # self.channel1.clear()
        # noise.render()

    def on_show_view(self) -> None:
        self.window.background_color = arcade.csscolor.BLACK

    def on_draw(self) -> bool | None:
        self.window.use()
        self.shadertoy.render(time=self.enter_time, time_delta=self.delta_time)

    def on_update(self, delta_time: float) -> bool | None:
        pass