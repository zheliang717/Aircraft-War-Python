import pygame
import random
from config import *

class Enemy(pygame.sprite.Sprite):
    """敌机类"""
    def __init__(self, type_key):
        super().__init__()
        self.type_key = type_key # 'small', 'mid', 'big'
        stats = ENEMY_STATS[type_key]
        
        self.hp = stats['hp']
        self.score_value = stats['score']
        self.prefix = stats['img_prefix']
        
        # 1. 加载图片素材
        self.images = []
        # 如果是大飞机，加载 n1, n2 实现飞行动画
        if type_key == 'big':
            for i in range(1, 3):
                path = os.path.join(IMG_DIR, f"{self.prefix}_n{i}.png")
                if os.path.exists(path):
                    self.images.append(pygame.image.load(path).convert_alpha())
        else:
            # 小/中飞机只加载一张静态图
            path = os.path.join(IMG_DIR, f"{self.prefix}.png")
            if os.path.exists(path):
                self.images.append(pygame.image.load(path).convert_alpha())

        # 容错：如果没图，用红色方块代替
        if not self.images:
            self.image = pygame.Surface((40,40))
            self.image.fill(RED)
        else:
            self.image = self.images[0]
            
        # 2. 初始化位置和速度
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.bottom = -random.randint(20, 50) # 从屏幕外上方随机位置出现
        self.speed = random.randint(stats['speed'][0], stats['speed'][1])
        
        # 3. 创建蒙版(Mask)用于精准碰撞检测
        self.mask = pygame.mask.from_surface(self.image)
        
        # 击中反馈相关
        self.hit_img = None
        hit_path = os.path.join(IMG_DIR, f"{self.prefix}_hit.png")
        if os.path.exists(hit_path):
            self.hit_img = pygame.image.load(hit_path).convert_alpha()
        self.hit_timer = 0
        self.anim_timer = 0
        self.frame_index = 0

    def update(self):
        """敌机移动和动画"""
        self.rect.y += self.speed
        
        # 飞行动画(针对大飞机)
        if len(self.images) > 1:
            now = pygame.time.get_ticks()
            if now - self.anim_timer > 200: # 每200ms切换一次
                self.anim_timer = now
                self.frame_index = (self.frame_index + 1) % len(self.images)
                # 只有在没被打中的时候才切图
                if not (self.hit_img and pygame.time.get_ticks() - self.hit_timer < 100):
                    self.image = self.images[self.frame_index]

        # 恢复被击中后的图片(Hit图只显示100ms)
        if self.hit_img and pygame.time.get_ticks() - self.hit_timer > 100:
            self.image = self.images[self.frame_index] if self.images else self.image
            
        # 移出屏幕销毁
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def hit(self, damage):
        """被子弹击中时调用"""
        self.hp -= damage
        if self.hit_img:
            self.image = self.hit_img
            self.hit_timer = pygame.time.get_ticks()
        return self.hp <= 0 # 返回 True 表示死亡

class Explosion(pygame.sprite.Sprite):
    """爆炸动画类"""
    def __init__(self, center, type_key):
        super().__init__()
        self.images = []
        prefix = ENEMY_STATS[type_key]['img_prefix']
        
        # 确定帧数(大飞机6帧，其他4帧)
        frame_count = 6 if type_key == 'big' else 4
        
        for i in range(1, frame_count + 1):
            path = os.path.join(IMG_DIR, f"{prefix}_down{i}.png")
            if os.path.exists(path):
                self.images.append(pygame.image.load(path).convert_alpha())
                
        self.image = self.images[0] if self.images else pygame.Surface((10,10))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 80 # 播放速度 (毫秒/帧)

    def update(self):
        """播放动画，播完自杀"""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame < len(self.images):
                self.image = self.images[self.frame]
            else:
                self.kill() # 彻底移除