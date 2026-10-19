"""全局音频（BGM / 音效），对应旧项目的 audio_player。"""

from __future__ import annotations

import arcade

from src.core.app_state import app_state
from src.core.resource_manager import res_manager


class AudioManager:
    def __init__(self):
        self._cache: dict[tuple[str, str], arcade.Sound | None] = {}
        self._music: arcade.Sound | None = None
        self._music_player = None
        self.current_music: str | None = None

    # ------------------------------------------------------------ 内部

    def _sound(self, category: str, name: str) -> arcade.Sound | None:
        key = (category, name)
        if key not in self._cache:
            try:
                self._cache[key] = res_manager.sound(category, name)
            except (FileNotFoundError, Exception):   # noqa: B014 - 音频缺失不应中断游戏
                self._cache[key] = None
        return self._cache[key]

    def _volume(self, scale: float = 1.0) -> float:
        return max(0.0, min(1.0, app_state.volume / 100.0 * scale))

    # ------------------------------------------------------------ 对外

    def play_music(self, name: str, volume: float = 0.6):
        """播放背景音乐（同一首不重复播放）。"""
        if self.current_music == name and self._is_playing():
            return
        self.stop_music()
        sound = self._sound("music", name)
        if sound is None:
            return
        try:
            self._music_player = sound.play(volume=self._volume(volume), loop=True)
            self.current_music = name
        except Exception:      # noqa: BLE001 - 无音频设备时静默
            self._music_player = None

    def _is_playing(self) -> bool:
        try:
            return self._music_player is not None and self._music_player.playing
        except Exception:      # noqa: BLE001
            return False

    def stop_music(self):
        if self._music_player is not None:
            try:
                self._music_player.pause()
                self._music_player.delete()
            except Exception:  # noqa: BLE001
                pass
        self._music_player = None
        self.current_music = None

    def play_sfx(self, name: str, volume: float = 0.6):
        sound = self._sound("ui", name)
        if sound is None:
            return
        try:
            sound.play(volume=self._volume(volume))
        except Exception:      # noqa: BLE001
            pass

    def touch(self):
        self.play_sfx("touch_button", 0.35)

    def press(self):
        self.play_sfx("press_button", 0.5)


audio = AudioManager()
