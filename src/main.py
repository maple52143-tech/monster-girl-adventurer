from pathlib import Path
import os
import arcade

from src.scenes.loading import Loading

arcade.resources.add_resource_handle("assets", os.path.join(Path(__file__).resolve().parent.parent, "assets"))

import core.settings as settings

def main():
    window = arcade.Window(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, "Monster Girl Adventurer")
    loading = Loading()
    window.show_view(loading)
    arcade.run()

if __name__ == "__main__":
    main()