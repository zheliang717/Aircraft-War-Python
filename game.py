import pygame
import sys
import random 
from config import *
from audio_manager import AudioManager
from sprites.hero import HeroPlane
from sprites.enemy import Enemy, Explosion
from sprites.bullet import Bullet
from sprites.powerup import PowerUp

class Game:
    """游戏主控类"""
    def __init__(self):
        # 1. 初始化引擎
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # 2. 加载资源
        self.audio = AudioManager()
        self.load_assets()
        
        # 3. 启动游戏
        self.reset_game()

    def load_assets(self):
        """加载背景、UI图标、字体"""
        try:
            self.bg_img = pygame.image.load(os.path.join(IMG_DIR, "background.png")).convert()
            self.bg_img = pygame.transform.scale(self.bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.pause_img = pygame.image.load(os.path.join(IMG_DIR, "pause.png")).convert_alpha()
            self.resume_img = pygame.image.load(os.path.join(IMG_DIR, "resume.png")).convert_alpha()
            self.bomb_img = pygame.image.load(os.path.join(IMG_DIR, "bomb.png")).convert_alpha()
        except:
            # 容错：如果图片缺失，生成色块
            self.bg_img = None
            self.pause_img = pygame.Surface((30, 30)); self.pause_img.fill((200, 200, 200))
            self.resume_img = pygame.Surface((30, 30)); self.resume_img.fill((200, 200, 200))
            self.bomb_img = pygame.Surface((30, 30)); self.bomb_img.fill(RED)

        # --- 字体加载 (尝试匹配系统中文) ---
        font_list = ["simhei", "microsoftyahei", "pingfangsc", "stheiti", "arial"]
        self.font_path = pygame.font.match_font(font_list[0])
        
        # 遍历列表，找到第一个可用的系统字体
        for f in font_list:
            match = pygame.font.match_font(f)
            if match:
                self.font_path = match
                break
        
        try:
            self.font = pygame.font.Font(self.font_path, 24)
            self.font_big = pygame.font.Font(self.font_path, 48)
        except:
            self.font = pygame.font.SysFont("arial", 24)
            self.font_big = pygame.font.SysFont("arial", 48)

    def reset_game(self):
        """重置/开始游戏数据"""
        self.state = "RUNNING" # 状态机: RUNNING, PAUSED, GAMEOVER
        self.score = 0
        
        # 创建精灵组(容器)
        self.all_sprites = pygame.sprite.Group() # 包含所有对象，用于统一draw
        self.enemies = pygame.sprite.Group()     # 敌机组，用于碰撞检测
        self.bullets = pygame.sprite.Group()     # 子弹组
        self.powerups = pygame.sprite.Group()    # 道具组
        
        # 创建英雄
        self.hero = HeroPlane(self.all_sprites, self.bullets)
        self.all_sprites.add(self.hero)
        
        self.audio.play_bgm()
        self.pause_rect = self.pause_img.get_rect()
        self.pause_rect.topright = (SCREEN_WIDTH - 10, 10)

    def spawn_enemy(self):
        """生成一架敌机"""
        r = random.randint(0, 100)
        # 概率控制：70%小飞机，20%中飞机，10%大飞机
        if r < 70:   t = 'small'
        elif r < 90: t = 'mid'
        else:        
            t = 'big'
            if self.hero.is_alive:
                self.audio.play_sound('enemy3_flying') # 大飞机出场播放音效
            
        e = Enemy(t)
        self.all_sprites.add(e)
        self.enemies.add(e)

    def use_bomb(self):
        """使用全屏炸弹"""
        if self.hero.bomb_count > 0:
            self.hero.bomb_count -= 1
            self.audio.play_sound('use_bomb')
            # 遍历所有敌机，全部销毁并加分
            for e in self.enemies:
                self.score += e.score_value
                expl = Explosion(e.rect.center, e.type_key)
                self.all_sprites.add(expl)
                e.kill()

    def handle_events(self):
        """事件监听循环"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # 鼠标点击处理
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "RUNNING":
                    # 检测点击暂停区域
                    if self.pause_rect.collidepoint(event.pos):
                        self.state = "PAUSED"
                        self.audio.play_sound('button')
                        pygame.mixer.music.pause()
                    # 鼠标右键 (3) 触发炸弹
                    elif event.button == 3: 
                        self.use_bomb()
                
                elif self.state == "PAUSED":
                    # 暂停中点击按钮 -> 恢复
                    if self.pause_rect.collidepoint(event.pos):
                        self.state = "RUNNING"
                        pygame.mixer.music.unpause()
                        
                elif self.state == "GAMEOVER":
                    # 结束后点击任意处 -> 重开
                    self.reset_game()

    def update(self):
        """游戏逻辑更新 (每帧执行)"""
        if self.state != "RUNNING": return

        # 1. 敌机生成策略
        # 分数越高，允许同屏存在的敌机越多
        target_count = 4 + self.score // 500 
        if len(self.enemies) < target_count:
            # 即使数量不够，也只有 3% 的概率生成，防止瞬间补满(平滑生成)
            if random.randint(0, 100) < 3: 
                self.spawn_enemy()

        self.all_sprites.update() # 调用所有精灵的 update 方法

        # 2. 碰撞检测：子弹 VS 敌机
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True, pygame.sprite.collide_mask)
        for enemy, bullets_hit in hits.items():
            for b in bullets_hit:
                if enemy.hit(b.damage): # 扣血，若死亡返回True
                    self.audio.play_sound(f'{enemy.type_key}_down')
                    self.score += enemy.score_value
                    # 生成爆炸
                    expl = Explosion(enemy.rect.center, enemy.type_key)
                    self.all_sprites.add(expl)
                    enemy.kill()
                    
                    # 随机掉落道具
                    drop_prob = 0.05 if enemy.type_key == 'small' else 0.4
                    if random.random() < drop_prob:
                        p = PowerUp(enemy.rect.center)
                        self.all_sprites.add(p)
                        self.powerups.add(p)
                    break 

        # 3. 碰撞检测：英雄 VS 敌机
        if self.hero.is_alive:
            hits = pygame.sprite.spritecollide(self.hero, self.enemies, False, pygame.sprite.collide_mask)
            if hits:
                self.hero.hit() # 英雄扣血/死亡
                self.audio.play_sound('game_over')
                for e in hits:
                    e.kill()
                    expl = Explosion(e.rect.center, e.type_key)
                    self.all_sprites.add(expl)

        # 4. 碰撞检测：英雄 VS 道具
        if self.hero.is_alive:
            hits = pygame.sprite.spritecollide(self.hero, self.powerups, True)
            for p in hits:
                if p.type == 'bomb':
                    self.audio.play_sound('get_bomb')
                    self.hero.power_up('bomb')
                else:
                    self.audio.play_sound('get_bullet')
                    self.hero.power_up('double')

        if not self.hero.alive():
            self.state = "GAMEOVER"

    def draw(self):
        """渲染绘制 (每帧执行)"""
        # 1. 画背景
        if self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill(BLACK)

        # 2. 画所有精灵
        self.all_sprites.draw(self.screen)

        # 3. 画 UI
        if self.state == "RUNNING" or self.state == "PAUSED":
            score_surf = self.font.render(f"得分: {self.score}", True, BLACK)
            self.screen.blit(score_surf, (10, 10))
            
            # 画炸弹
            self.screen.blit(self.bomb_img, (10, SCREEN_HEIGHT - 60))
            bomb_text = self.font.render(f"x {self.hero.bomb_count}", True, BLACK)
            self.screen.blit(bomb_text, (70, SCREEN_HEIGHT - 50))
            
            # 画暂停按钮
            img = self.pause_img if self.state == "RUNNING" else self.resume_img
            self.screen.blit(img, self.pause_rect)
            
            if self.state == "PAUSED":
                pause_text = self.font_big.render("游戏暂停", True, RED)
                text_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.screen.blit(pause_text, text_rect)

        if self.state == "GAMEOVER":
            over_surf = self.font_big.render("游戏结束", True, BLACK)
            score_surf = self.font.render(f"最终得分: {self.score}", True, BLACK)
            restart_surf = self.font.render("点击屏幕任意处重新开始游戏", True, RED)
            
            center_x = SCREEN_WIDTH // 2
            self.screen.blit(over_surf, over_surf.get_rect(center=(center_x, 200)))
            self.screen.blit(score_surf, score_surf.get_rect(center=(center_x, 280)))
            self.screen.blit(restart_surf, restart_surf.get_rect(center=(center_x, 380)))

        # 4. 翻转缓冲区(显示画面)
        pygame.display.flip()

    def run(self):
        """主循环入口"""
        while True:
            self.clock.tick(FPS) # 强制 60 FPS
            self.handle_events()
            self.update()
            self.draw()