import pygame
import random

# 初始化 Pygame
pygame.init()

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)    # I型方块
YELLOW = (255, 255, 0)  # O型方块
PURPLE = (255, 0, 255)  # T型方块
GREEN = (0, 255, 0)     # S型方块
RED = (255, 0, 0)       # Z型方块
BLUE = (0, 0, 255)      # J型方块
ORANGE = (255, 165, 0)  # L型方块

# 游戏区域设置
BLOCK_SIZE = 30  # 每个方块的大小
GRID_WIDTH = 10  # 游戏区域宽度（以方块数计）
GRID_HEIGHT = 20 # 游戏区域高度（以方块数计）

# 设置游戏窗口
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8)  # 游戏区域加上右侧信息区
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('俄罗斯方块')

# 创建游戏时钟
clock = pygame.time.Clock()

# 定义方块形状
SHAPES = [
    [[1, 1, 1, 1]], # I
    [[1, 1], [1, 1]], # O
    [[0, 1, 0], [1, 1, 1]], # T
    [[0, 1, 1], [1, 1, 0]], # S
    [[1, 1, 0], [0, 1, 1]], # Z
    [[1, 0, 0], [1, 1, 1]], # J
    [[0, 0, 1], [1, 1, 1]]  # L
]

# 定义方块颜色
SHAPE_COLORS = [CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE] 

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.game_over = False
        self.score = 0
        self.new_piece()
    
    def new_piece(self):
        # 随机选择一个新的方块
        shape = random.choice(SHAPES)
        self.current_piece = {
            'shape': shape,
            'color': SHAPE_COLORS[SHAPES.index(shape)],
            'x': GRID_WIDTH // 2 - len(shape[0]) // 2,
            'y': 0
        }
        
        # 检查游戏是否结束
        if self.check_collision():
            self.game_over = True
    
    def check_collision(self):
        shape = self.current_piece['shape']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.current_piece['x'] + x
                    new_y = self.current_piece['y'] + y
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or 
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return True
        return False
    
    def move(self, dx, dy):
        self.current_piece['x'] += dx
        self.current_piece['y'] += dy
        if self.check_collision():
            self.current_piece['x'] -= dx
            self.current_piece['y'] -= dy
            if dy > 0:  # 如果是向下移动发生碰撞，则固定方块
                self.freeze_piece()
                self.clear_lines()
                self.new_piece()
            return False
        return True
    
    def rotate(self):
        # 保存当前形状
        old_shape = self.current_piece['shape']
        # 旋转方块（矩阵转置后反转每一行）
        self.current_piece['shape'] = [
            [old_shape[y][x] for y in range(len(old_shape)-1, -1, -1)]
            for x in range(len(old_shape[0]))
        ]
        # 如果旋转后发生碰撞，则恢复原状
        if self.check_collision():
            self.current_piece['shape'] = old_shape

    def freeze_piece(self):
        shape = self.current_piece['shape']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece['y'] + y][self.current_piece['x'] + x] = self.current_piece['color']

    def clear_lines(self):
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(self.grid[y]):
                lines_cleared += 1
                for y2 in range(y, 0, -1):
                    self.grid[y2] = self.grid[y2-1][:]
                self.grid[0] = [0] * GRID_WIDTH
            else:
                y -= 1
        # 更新分数
        if lines_cleared:
            self.score += (1, 2, 5, 10)[lines_cleared-1] * 100

def draw_grid(screen, grid):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, cell,
                               (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                BLOCK_SIZE-1, BLOCK_SIZE-1))

def draw_piece(screen, piece):
    shape = piece['shape']
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, piece['color'],
                               ((piece['x'] + x) * BLOCK_SIZE,
                                (piece['y'] + y) * BLOCK_SIZE,
                                BLOCK_SIZE-1, BLOCK_SIZE-1))

def main():
    game = Tetris()
    fall_time = 0
    fall_speed = 50  # 正常下落速度
    fast_fall_speed = 5  # 加速下落速度
    current_speed = fall_speed  # 当前下落速度
    
    while True:
        # 处理游戏退出
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game.move(1, 0)
                elif event.key == pygame.K_DOWN:
                    current_speed = fast_fall_speed  # 按下向下键时加速
                elif event.key == pygame.K_UP:
                    game.rotate()
                elif event.key == pygame.K_SPACE:
                    while game.move(0, 1):
                        pass
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    current_speed = fall_speed  # 松开向下键时恢复正常速度
        
        # 方块自动下落
        fall_time += 1
        if fall_time >= current_speed:  # 使用当前速度控制下落
            game.move(0, 1)
            fall_time = 0
        
        # 绘制游戏界面
        screen.fill(BLACK)
        draw_grid(screen, game.grid)
        if game.current_piece:
            draw_piece(screen, game.current_piece)
        
        # 显示分数
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {game.score}', True, WHITE)
        screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + 10, 10))
        
        # 游戏结束处理
        if game.game_over:
            game_over_text = font.render('Game Over!', True, WHITE)
            screen.blit(game_over_text, (GRID_WIDTH * BLOCK_SIZE + 10, 50))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()