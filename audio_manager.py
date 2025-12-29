import pygame
import os
from config import *

class AudioManager:
    """音频管理器：统一处理背景音乐和音效"""
    def __init__(self):
        self.sounds = {}
        # 只有在 Pygame 音频模块初始化成功后才工作
        if pygame.mixer.get_init():
            self.load_resources()

    def load_resources(self):
        """加载音效文件到内存"""
        # 字典映射： 代码调用名 -> 文件名
        sound_map = {
            'bullet': 'bullet.wav',
            'enemy1_down': 'enemy1_down.wav',
            'enemy2_down': 'enemy2_down.wav',
            'enemy3_down': 'enemy3_down.wav',
            'game_over': 'me_down.wav',
            'get_bomb': 'get_bomb.wav',
            'get_bullet': 'get_bullet.wav',
            'supply': 'supply.wav',
            'use_bomb': 'use_bomb.wav',
            'button': 'button.wav',
            'enemy3_flying': 'enemy3_flying.wav',
        }
        
        for key, filename in sound_map.items():
            path = os.path.join(SND_DIR, filename)
            # 检查文件是否存在，存在才加载
            if os.path.exists(path):
                self.sounds[key] = pygame.mixer.Sound(path)
                self.sounds[key].set_volume(0.5) # 设置默认音量 50%

    def play_bgm(self):
        """播放背景音乐 (循环)"""
        path = os.path.join(SND_DIR, 'game_music.wav')
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(0.2) # 背景音稍微小一点
                pygame.mixer.music.play(-1) # -1 表示无限循环
            except Exception as e:
                print(f"BGM加载失败: {e}")

    def play_sound(self, key):
        """播放指定音效"""
        if key in self.sounds:
            self.sounds[key].play()