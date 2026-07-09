from pathlib import Path
from functools import lru_cache
import os
import json
import arcade

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

    def image(self, name: str):
        file = search_res(Path(os.path.join(self.res_dir, "images")), name)
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

res_manager = ResourceManager()


