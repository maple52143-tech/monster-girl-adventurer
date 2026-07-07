from pathlib import Path
import os
import arcade

from src.scenes.loading import Loading
from src.core.game_window import GameWindow

arcade.resources.add_resource_handle("assets", os.path.join(Path(__file__).resolve().parent.parent, "assets"))

import core.settings as settings

def main():
    window = GameWindow(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, "Monster Girl Adventurer")
    window.auto_register(Path(os.path.join(Path(__file__).resolve().parent, "scenes")))
    window.switch_scene("loading")
    arcade.run()

if __name__ == "__main__":
    main()