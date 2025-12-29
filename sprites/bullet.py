import pygame
from config import *

class Bullet(pygame.sprite.Sprite):
    """子弹类：继承自 Sprite"""
    def __init__(self, x, y, is_enhanced=False):
        super().__init__()
        # is_enhanced: 是否是加强版子弹(红色)
        
        try:
            # 根据是否加强加载不同图片
            img_name = "bullet2.png" if is_enhanced else "bullet1.png"
            self.image = pygame.image.load(os.path.join(IMG_DIR, img_name)).convert_alpha()
        except:
            # 如果没图，画个矩形代替
            self.image = pygame.Surface((5, 15))
            self.image.fill(YELLOW if is_enhanced else list(BLUE))
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = BULLET_SPEED
        self.damage = 2 if is_enhanced else 1 # 加强版伤害更高

    def update(self):
        """每帧调用：向上移动"""
        self.rect.y += self.speed_y
        # 如果飞出屏幕上方(小于0)，则销毁对象释放内存
        if self.rect.bottom < 0:
            self.kill()