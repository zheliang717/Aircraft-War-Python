import pygame
from config import *
from sprites.bullet import Bullet

class HeroPlane(pygame.sprite.Sprite):
    """玩家英雄飞机"""
    def __init__(self, all_sprites, bullets_group):
        super().__init__()
        self.all_sprites = all_sprites # 引用总精灵组
        self.bullets_group = bullets_group # 引用子弹组
        
        # 游戏属性
        self.hp = 1
        self.is_alive = True
        self.bomb_count = 0
        self.fire_level = 1 # 当前火力等级 (1-5)
        self.powerup_timer = 0 # 道具计时器
        
        # 射击控制
        self.last_shot_time = 0
        self.shoot_delay = 150 # 射击间隔 (毫秒)
        
        # 加载正常飞行图 (me1.png, me2.png 喷气效果)
        self.imgs_fly = []
        for i in range(1, 3):
            path = os.path.join(IMG_DIR, f"me{i}.png")
            if os.path.exists(path):
                self.imgs_fly.append(pygame.image.load(path).convert_alpha())
        
        # 加载坠毁图
        self.imgs_die = []
        for i in range(1, 5):
            path = os.path.join(IMG_DIR, f"me_destroy_{i}.png")
            if os.path.exists(path):
                self.imgs_die.append(pygame.image.load(path).convert_alpha())

        self.image = self.imgs_fly[0] if self.imgs_fly else pygame.Surface((60,80))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.mask = pygame.mask.from_surface(self.image)
        
        # 动画变量
        self.anim_timer = 0
        self.frame_index = 0
        self.die_frame_index = 0
        self.die_timer = 0

    def update(self):
        """逻辑更新"""
        if not self.is_alive:
            self.play_death_anim()
            return

        # 1. 鼠标跟随
        pos = pygame.mouse.get_pos()
        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]
        self.constrain_movement()

        # 2. 检测鼠标左键按下 -> 射击
        if pygame.mouse.get_pressed()[0]: 
            self.shoot()

        # 3. 播放喷气动画
        self.animate_fly()
        
        # 4. 检查道具是否过期
        self.check_powerup()

    def constrain_movement(self):
        """限制飞机不飞出屏幕"""
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT

    def animate_fly(self):
        """切换 me1 和 me2"""
        if not self.imgs_fly: return
        now = pygame.time.get_ticks()
        if now - self.anim_timer > 100:
            self.anim_timer = now
            self.frame_index = (self.frame_index + 1) % len(self.imgs_fly)
            self.image = self.imgs_fly[self.frame_index]

    def shoot(self):
        """核心射击逻辑：根据等级计算子弹位置"""
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_delay:
            self.last_shot_time = now
            
            # 偏移量列表：0代表中间，负数左边，正数右边
            bullet_offsets = []
            
            if self.fire_level == 1:
                bullet_offsets = [0]
            elif self.fire_level == 2:
                bullet_offsets = [-20, 20]
            elif self.fire_level == 3:
                bullet_offsets = [-25, 0, 25]
            elif self.fire_level == 4:
                bullet_offsets = [-35, -12, 12, 35]
            elif self.fire_level >= 5:
                bullet_offsets = [-40, -20, 0, 20, 40]

            for offset in bullet_offsets:
                # 等级>=3时，两侧子弹变为加强版
                is_enhanced = (self.fire_level >= 3)
                b = Bullet(self.rect.centerx + offset, self.rect.centery, is_enhanced)
                self.all_sprites.add(b)
                self.bullets_group.add(b)

    def power_up(self, p_type):
        """吃到道具的回调"""
        if p_type == 'double':
            # 增加火力等级，最高MAX_FIRE_LEVEL
            self.fire_level = min(self.fire_level + 1, MAX_FIRE_LEVEL)
            self.powerup_timer = pygame.time.get_ticks()
        elif p_type == 'bomb':
            # 增加炸弹，上限3个
            self.bomb_count = min(self.bomb_count + 1, 3)

    def check_powerup(self):
        """检查道具持续时间，超时则降级"""
        if self.fire_level > 1:
            if pygame.time.get_ticks() - self.powerup_timer > POWERUP_TIME:
                self.fire_level -= 1 
                self.powerup_timer = pygame.time.get_ticks() # 重置计时，每10秒降一级，而不是一下子变回1级

    def hit(self):
        """英雄被击中"""
        self.hp -= 1
        if self.hp <= 0:
            self.is_alive = False
            self.die_timer = pygame.time.get_ticks()

    def play_death_anim(self):
        """播放死亡动画"""
        now = pygame.time.get_ticks()
        if now - self.die_timer > 100:
            self.die_timer = now
            if self.die_frame_index < len(self.imgs_die):
                self.image = self.imgs_die[self.die_frame_index]
                self.die_frame_index += 1
            else:
                self.kill() # 动画放完，彻底销毁