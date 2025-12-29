import pygame
import random
from config import *

class PowerUp(pygame.sprite.Sprite):
    """道具补给包"""
    def __init__(self, center):
        super().__init__()
        # 随机决定类型：30%概率是炸弹(bomb)，70%是双倍子弹(double)
        self.type = 'bomb' if random.random() < 0.3 else 'double'
        
        img_name = "bomb_supply.png" if self.type == 'bomb' else "bullet_supply.png"
        try:
            self.image = pygame.image.load(os.path.join(IMG_DIR, img_name)).convert_alpha()
        except:
            self.image = pygame.Surface((30,30))
            self.image.fill(GREEN)
            
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed = 3 # 下落速度

    def update(self):
        """向下移动，超出屏幕销毁"""
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()