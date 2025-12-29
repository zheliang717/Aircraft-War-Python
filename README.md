# 飞机大战游戏开发项目README

# ✈️ 飞机大战游戏开发项目报告

## 1. 项目的意义与目的

### 1.1 飞机大战项目目的

本项目旨在利用 Python 编程语言结合 Pygame 游戏开发库，构建一款功能完整、交互流畅的 2D 飞行射击游戏。主要开发目的包括：

- **技术实践**：深入理解面向对象编程（OOP）思想，掌握类（Class）的继承与封装。

- **引擎掌握**：熟练掌握 Pygame 的核心模块，包括 Sprite 精灵管理、Event 事件监听及 Surface 图形渲染。

- **逻辑构建**：实现复杂的业务逻辑，如基于权重的敌机生成算法、火力等级系统及状态机管理。

### 1.2 飞机大战项目意义

- **教育意义**：本项目是计算机图形学与交互设计的经典入门案例，能直观展示代码如何驱动视觉反馈。

- **应用价值**：复刻经典玩法，提供解压的娱乐体验，同时具备良好的代码扩展性，为后续开发（如网络对战版）奠定基础。

## 2. 系统功能描述

### 2.1 游戏框架搭建

采用“初始化-主循环-退出”的经典架构。通过 Game 类管理全局状态，利用 pygame.time.Clock 控制游戏帧率稳定在 60FPS。

**核心代码展示（主循环逻辑）**：

```Python

def run(self):
    while True:
        # 控制帧率，确保游戏在不同电脑上速度一致
        self.clock.tick(FPS)
        # 1. 处理输入事件（键盘/鼠标/退出）
        self.handle_events()
        # 2. 更新游戏数据（位置/状态/碰撞）
        self.update()
        # 3. 渲染画面到屏幕
        self.draw()
```

### 2.2 游戏背景和英雄飞机

背景采用双图交替滚动实现无限延伸效果；英雄飞机放弃了传统的键盘控制，改为鼠标跟随模式，并实现了基于等级的子弹发射系统。

**核心代码展示（鼠标跟随与背景滚动）**：

```Python

# 英雄飞机跟随鼠标
def update(self):
    pos = pygame.mouse.get_pos()
    self.rect.centerx = pos[0]
    self.rect.centery = pos[1]
    self.constrain_movement() # 边界限制

# 背景滚动渲染
def draw(self):
    # 绘制两张背景图实现无缝连接
    self.screen.blit(self.bg_img, (0, self.bg_y))
    self.screen.blit(self.bg_img, (0, self.bg_y - SCREEN_HEIGHT))
    self.bg_y = (self.bg_y + 2) % SCREEN_HEIGHT
```

### 2.3 指示器面板（UI）

解决了 Pygame 不支持中文的痛点，通过系统字体匹配机制加载中文字体，实时显示得分和炸弹数量。

**核心代码展示（中文支持与UI绘制）**：

```Python

# 字体加载策略
font_list = ["simhei", "microsoftyahei", "pingfangsc", "arial"]
self.font_path = pygame.font.match_font(font_list[0]) # 自动寻找系统字体
self.font = pygame.font.Font(self.font_path, 24)

# 绘制中文得分
score_surf = self.font.render(f"得分: {self.score}", True, BLACK)
self.screen.blit(score_surf, (10, 10))
```

### 2.4 逐帧动画和飞机类

所有飞机和特效均继承自 pygame.sprite.Sprite。通过时间差（Delta Time）计算来切换图片帧，实现喷气和爆炸效果。

**核心代码展示（动画状态机）**：

```Python

# 爆炸动画更新逻辑
def update(self):
    now = pygame.time.get_ticks()
    # 每 80ms 切换一帧图片
    if now - self.last_update > self.frame_rate:
        self.last_update = now
        self.frame += 1
        if self.frame < len(self.images):
            self.image = self.images[self.frame]
        else:
            self.kill() # 动画播放完毕，销毁对象
```

### 2.5 碰撞检测

为了提升手感，使用了 pygame.mask 模块进行像素级碰撞检测，只有当非透明区域重叠时才判定为碰撞。

**核心代码展示（像素级碰撞）**：

```Python

# 子弹击中敌机检测
# collide_mask 实现了基于透明度的像素级检测
hits = pygame.sprite.groupcollide(
    self.enemies, 
    self.bullets, 
    False, 
    True, 
    pygame.sprite.collide_mask
)

for enemy, bullets_hit in hits.items():
    if enemy.hit(bullets_hit[0].damage): # 扣血逻辑
        enemy.kill()
```

### 2.6 音乐和音效

封装了 AudioManager 类，支持背景音乐循环播放和音效的即时触发，并包含资源缺失的容错处理。

**核心代码展示（音效管理）**：

```Python

class AudioManager:
    def load_resources(self):
        sound_files = {'shoot': 'bullet.wav', 'bomb': 'use_bomb.wav'}
        for name, file in sound_files.items():
            path = os.path.join(SND_DIR, file)
            if os.path.exists(path):
                self.sounds[name] = pygame.mixer.Sound(path)

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()
```

### 2.7 项目打包

通过 PyInstaller 进行打包，核心在于解决资源路径在开发环境与打包环境（临时目录）不一致的问题。

**核心代码展示（路径适配）**：

```Python

import sys
import os

# 判断是否在 PyInstaller 打包后的环境中运行
if getattr(sys, 'frozen', False):
    # 使用解压后的临时目录
    BASE_DIR = sys._MEIPASS
else:
    # 使用当前脚本所在目录
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMG_DIR = os.path.join(BASE_DIR, "assets", "images")
```

## 3. 项目总结

本项目成功开发了一款高完成度的 Python 飞机大战游戏。通过模块化设计，我们将游戏逻辑、渲染、音频和资源管理分离，保证了代码的健壮性。

在功能实现上，我们不仅完成了基础的飞行射击，还攻克了像素级碰撞检测、平滑敌机生成算法、中文界面显示以及可执行文件打包等技术难点。最终生成的 .exe 文件运行流畅，无内存泄漏，交互体验良好，达到了预期的开发目标。
