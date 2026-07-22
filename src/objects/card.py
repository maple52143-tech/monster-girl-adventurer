import arcade

from src.core.resource_manager import res_manager
from src.core.status_manager import status_manager
from src.core.illustration_manager import illu_manager

class Card(arcade.Sprite):
    def __init__(self, name: str, owner):
        t, self.data = res_manager.card(name)
        super().__init__(t, 0.13)

        self.owner = owner
        self.effects = []
        for name, value in self.data['effect'].items():
            self.effects.append([res_manager.effect(name), value[0], value[1]])

    def use_card(self):
        for e in self.effects:
            match e[2]:
                case "enemy":
                    enemy = status_manager.enemy[status_manager.enemy_ptr]
                    enemy.effects.append(e[0](enemy, e[1]))
                case "self":
                    self.owner.effects.append(e[0](self.owner, e[1]))
                case "team":
                    team = status_manager.team[status_manager.team_ptr]
                    team.effects.append(e[0](team, e[1]))
        status_manager.check_effect()
        for e in self.owner.effects:
            e.on_action()
        illu_manager.change_illu("no", self.owner, 0.6, "attack")
        if self.owner.type == 'character':
            self.owner.hand.remove(self)
            self.owner.discard_pile.append(self)