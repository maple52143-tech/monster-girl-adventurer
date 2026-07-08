import arcade

from src.core.resource_manager import res_manager


class Character:
    def __init__(self, name):
        self.illustration = res_manager.image(f"illustration_{name}")
        self.avatar = res_manager.image(f"avatar_{name}")

        self.data, self.type = res_manager.data(name)
        self.name = self.data["name"]
        self.introduction = self.data["introduction"]

        self.max_hp = self.data['initial_status']['max_hp']
        self.max_mp = self.data['initial_status']['max_mp']
        self.hp = self.max_hp
        self.mp = self.max_mp / 2

        self.shield = 0.0