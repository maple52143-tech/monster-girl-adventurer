import arcade
from arcade.future.light import Light, LightLayer
from arcade.experimental.shadertoy import Shadertoy
from arcade.gl.framebuffer import Framebuffer

from src.core.resource_manager import res_manager
from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.game_window import GameWindow

class Loading(arcade.View):
    def __init__(self, window: GameWindow):
        super().__init__(window=window)
        self.sprites = arcade.SpriteList()
        self.title = arcade.Sprite(res_manager.image("sign"), scale=1.2, center_x=800, center_y=450)
        self.sprites.append(self.title)

        self.sound = res_manager.sound("music", "loading")

        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.light = Light(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 800, mode="soft")

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

        self.shadertoy = Shadertoy(window_size, res_manager.shader("cloud"))

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
        noise = Shadertoy(window_size, res_manager.shader("rgba_noise"))
        self.channel0.use()
        self.channel0.clear()
        noise.render()
        self.channel1.use()
        self.channel1.clear()
        noise.render()


    def on_show_view(self) -> None:
        self.window.background_color = arcade.csscolor.BLACK
        self.play_back = self.sound.play(0.5)

    def on_draw(self) -> bool | None:
        # self.channel0.use()
        # self.channel0.clear(color=arcade.color.BLACK)
        # self.sprites.draw()
        #
        #
        # self.window.use()
        # self.clear()
        self.window.use()
        self.shadertoy.render(time=self.enter_time, time_delta=self.delta_time)
        self.sprites.draw()



    def on_update(self, delta_time: float) -> bool | None:
        self.enter_time += delta_time
        self.delta_time = delta_time
        self.sprites.update()

        if self.enter_time >= 0.9 and not self.lighted:
            self.light_layer.add(self.light)
            self.lighted = True
        if self.enter_time >= 5.0:
            arcade.stop_sound(self.play_back)
            self.window.switch_scene("menu")




