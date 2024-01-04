import pygame
import random
from enum import Enum

pygame.init()

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 10
SPEED = 10

class Snake:
    def __init__(self, dir, posX, posY):
        # init direction
        self.direction = dir

         # init pos and length
        self.head = (posX, posY)
        self.body = [self.head,
                      (self.head[0] - BLOCK_SIZE, self.head[1] - BLOCK_SIZE),
                      (self.head[0] - 2*BLOCK_SIZE, self.head[1] - 2*BLOCK_SIZE)]
        
    def move(self):
        (x, y) = self.head
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        else:
            y -= BLOCK_SIZE
        self.head = (x, y)
        
    def getDir(self):
        return self.direction
    
    def setDir(self, dir):
        self.direction = dir

    def getBody(self):
        return self.body
    
    def setBody(self, body):
        self.body = body

    def getHead(self):
        return self.head
        

class SnakeGame:

    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height

        # init display
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()

        # init snake
        self.snake = Snake(Direction.RIGHT, self.width/2, self.height/2)

        # init game state
        self.score = 0
        self.food = None
        self.placeFood()
    
    def placeFood(self):
        x = random.randint(0, self.width//BLOCK_SIZE - 1)
        y = random.randint(0, self.height//BLOCK_SIZE - 1)
        self.food = (x*BLOCK_SIZE, y*BLOCK_SIZE)
        if self.food in self.snake.body:
            self.placeFood()
    
    def game_step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.snake.setDir(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.snake.setDir(Direction.RIGHT)
                elif event.key == pygame.K_UP:
                    self.snake.setDir(Direction.UP)
                elif event.key == pygame.K_DOWN:
                    self.snake.setDir(Direction.DOWN)
        
        self.snake.move()
        self.snake.getBody().insert(0, self.snake.getHead())
        
        gameOver = False
        if self.isCollision():
            gameOver = True
            return gameOver, self.score
        
        if self.snake.getHead() == self.food:
            self.score += 1
            self.placeFood()
        else:
            self.snake.getBody().pop()
        
        self.display.fill(BLACK)
        for pt in self.snake.getBody():
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt[0], pt[1], BLOCK_SIZE, BLOCK_SIZE))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food[0], self.food[1], BLOCK_SIZE, BLOCK_SIZE))

        pygame.display.flip()

        self.clock.tick(SPEED)

        return gameOver, self.score
        
    
    def isCollision(self):
        if self.snake.getHead()[0] < 0 or self.snake.getHead()[0] > self.width - BLOCK_SIZE or self.snake.getHead()[1] < 0 or self.snake.getHead()[1] > self.height - BLOCK_SIZE:
            return True
        
        if self.snake.getHead() in self.snake.getBody()[1:]:
            return True
        
        return False
    
if __name__ == '__main__':
    game = SnakeGame()
    
    # game loop
    while True:
        game_over, score = game.game_step()
        
        if game_over == True:
            break
        
    print('Final Score', score)
        
        
    pygame.quit()