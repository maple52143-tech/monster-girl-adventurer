import importlib.util
import inspect
from typing import Dict, Type
from pathlib import Path
import logging
import arcade


class GameWindow(arcade.Window):
    def __init__(self, width, height, title: str):
        super().__init__(width, height, title)

        self.scenes: Dict[str, arcade.View] = {}
        self.current_scene_name: str = None

    def register_scene(self, name: str, scene: arcade.View):
        self.scenes[name] = scene
        if scene.window is None:
            scene.window = self

    def auto_register(self, path: Path):
        p = path

        for py_file in p.glob("*.py"):
            if py_file.name == "__init__.py":
                continue

            module_name = py_file.stem
            spec = importlib.util.spec_from_file_location(
                f"src.scenes.{module_name}", py_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if not issubclass(obj, arcade.View) or obj is arcade.View:
                    continue
                # 只注册「本模块里定义」的场景类：场景文件会 import 基类
                # （如 UIScene），否则基类也会被当成一个场景实例化。
                if obj.__module__ != module.__name__:
                    continue
                scene_name = obj.__name__.lower()
                self.register_scene(scene_name, obj(self))
                logging.info(f"successfully register scene: {scene_name}")


    def switch_scene(self, name: str) -> None:
        if name in self.scenes:
            self.current_scene_name = name
            self.show_view(self.scenes[name])
        else:
            raise KeyError(f"场景 {name} 不存在。")

    def get_scene(self, name: str) -> arcade.View:
        return self.scenes.get(name)
