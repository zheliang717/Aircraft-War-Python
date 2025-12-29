import os
import sys

# ====================================================
# 1. 路径配置 (最关键部分)
# ====================================================
# getattr(sys, 'frozen', False) 用于判断当前是否是打包后的 exe 环境
# 如果是 exe，sys._MEIPASS 是解压后的临时目录；否则使用当前文件目录
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 拼接资源目录，确保跨平台(Windows/Mac)路径兼容
IMG_DIR = os.path.join(BASE_DIR, "assets", "images")
SND_DIR = os.path.join(BASE_DIR, "assets", "audio")

# ====================================================
# 2. 屏幕与基础设置
# ====================================================
SCREEN_WIDTH = 480       # 屏幕宽度
SCREEN_HEIGHT = 700      # 屏幕高度
FPS = 60                 # 帧率 (Frames Per Second)
TITLE = "飞机大战" # 窗口标题

# ====================================================
# 3. 颜色定义 (RGB格式)
# ====================================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# ====================================================
# 4. 游戏数值平衡
# ====================================================
HERO_HP = 1              # 英雄血量 (一碰就死模式)
BULLET_SPEED = -12       # 子弹向上飞，所以Y轴是负数
POWERUP_TIME = 10000     # 道具持续时间 (10秒)
MAX_FIRE_LEVEL = 5       # 最大火力等级 (5级扇形散弹)

# 敌机属性配置字典：
# hp: 血量, speed: 速度范围, score: 击杀得分, img_prefix: 图片文件前缀
ENEMY_STATS = {
    'small': {'hp': 1, 'speed': (2, 4), 'score': 100, 'img_prefix': 'enemy1'}, 
    'mid':   {'hp': 6, 'speed': (1, 3), 'score': 500, 'img_prefix': 'enemy2'}, 
    'big':   {'hp': 15, 'speed': (1, 2), 'score': 2000, 'img_prefix': 'enemy3'}
}