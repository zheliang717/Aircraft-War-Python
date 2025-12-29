import sys
# 确保可以引用到模块
sys.path.append('.') 
from game import Game

if __name__ == "__main__":
    game = Game()
    game.run()