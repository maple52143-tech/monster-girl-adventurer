from pathlib import Path
import os
import arcade

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

res_manager = ResourceManager()


