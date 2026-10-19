import importlib.util
import inspect
from pathlib import Path
from functools import lru_cache
import os
import json
from typing import LiteralString

import arcade

from src.core.settings import HOME
from src.effect.standard import StandardEffect

@lru_cache(maxsize=1024)
def search_res(path: Path, name: str):
    pattern = f"{name}.*"
    matches = list(path.rglob(pattern))

    if not matches:
        return None
    else:
        return matches[0]

class ResourceManager:
    def __init__(self):
        self.res_dir = os.path.join(Path(__file__).resolve().parent.parent.parent, "assets")
        self._effect_cache: dict[str, type] = {}

    def image(self, name: str, other_dir: LiteralString = ""):
        file = search_res(Path(os.path.join(self.res_dir, "images", other_dir)), name)
        if file is None:
            raise FileNotFoundError(f"图片文件不存在: {name}")

        return file

    def sound(self, type: str, name: str):
        file = search_res(Path(os.path.join(self.res_dir, "sounds", type)), name)
        if file is None:
            raise FileNotFoundError(f"音频文件不存在: {type} / {name}")

        return arcade.load_sound(file)

    def data(self, name: str):
        file = search_res(Path(os.path.join(self.res_dir, "data")), name)
        if file is None:
            raise FileNotFoundError(f"数据文件不存在: {name}")

        with open(file, "r", encoding='utf-8') as f:
            data = json.load(f)

        return data, file.parent.name

    def card(self, name: str):
        image_file = search_res(Path(os.path.join(self.res_dir, "images", "card")), name)
        if image_file is None:
            raise FileNotFoundError(f"卡面文件不存在: {name}")

        data_file, _ = self.data(f"card_{name}")

        return image_file, data_file

    @staticmethod
    def _load_module(module_name: str, file):
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def effect(self, name: str, strict: bool = False):
        """加载 src/effect/<name>.py 中的效果类。

        优先取模块里显式声明的 EFFECT_CLASS；
        否则回退到旧规则（模块内定义、类名以 Effect 结尾、且是 StandardEffect 子类），
        此时若出现一个以上候选会直接报错——旧实现按字母序取第一个，会静默拿错类。
        """
        if name in self._effect_cache:
            return self._effect_cache[name]

        file = search_res(Path(os.path.join(HOME, "src", "effect")), name)
        if file is None:
            raise FileNotFoundError(f"效果文件不存在: {name}")

        module = self._load_module(f"src.effect.{name}", file)

        cls = getattr(module, "EFFECT_CLASS", None)
        if cls is None and strict:
            raise LookupError(f"效果 {name} 需要在模块中声明 EFFECT_CLASS")

        if cls is None:
            candidates = []
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if not obj.__name__.endswith("Effect"):
                    continue
                if obj.__module__ != module.__name__:   # 排除 import 进来的基类/其它效果
                    continue
                if not isinstance(obj, type) or not issubclass(obj, StandardEffect):
                    continue
                candidates.append(obj)

            if len(candidates) > 1:
                names = ", ".join(c.__name__ for c in candidates)
                raise RuntimeError(
                    f"效果 {name} 有多个候选类（{names}），请在模块中声明 EFFECT_CLASS"
                )

            cls = candidates[0] if candidates else None

        if cls is None:
            raise LookupError(f"效果 {name} 中没有找到可用的效果类")

        self._effect_cache[name] = cls
        return cls

    def shader(self, name: str):
        shader_file = search_res(Path(os.path.join(self.res_dir, "shaders")), name)
        if shader_file is None:
            raise FileNotFoundError(f"着色器文件不存在: {name}")

        with open(shader_file, 'r', encoding='utf-8') as f:
            shader = f.read()
        return shader

res_manager = ResourceManager()


