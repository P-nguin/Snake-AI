import torch
import random
import numpy as np
from collections import deque
from snake import SnakeGame, Direction
from model import Linear_QNet, QTrainer
from plotHelper import plot

MAX_MEMORY = 500_000
BATCH_SIZE = 5000
LR = 0.001

class Agent:
    def __init__(self) -> None:
        self.number_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def getState(self, game):
        head = game.snake.getHead()
        point_l = (head[0] - game.getBlockSize(), head[1])
        point_r = (head[0] + game.getBlockSize(), head[1])
        point_u = (head[0], head[1] - game.getBlockSize())
        point_d = (head[0], head[1] + game.getBlockSize())

        dir_l = game.snake.getDir() == Direction.LEFT
        dir_r = game.snake.getDir() == Direction.RIGHT
        dir_u = game.snake.getDir() == Direction.UP
        dir_d = game.snake.getDir() == Direction.DOWN

        dangerS = (dir_r and game.isCollision(point_r)) or (dir_l and game.isCollision(point_l)) or (dir_u and game.isCollision(point_u)) or (dir_d and game.isCollision(point_d))
        dangerL = (dir_d and game.isCollision(point_r)) or (dir_u and game.isCollision(point_l)) or (dir_r and game.isCollision(point_u)) or (dir_l and game.isCollision(point_d))
        dangerR = (dir_u and game.isCollision(point_r)) or (dir_d and game.isCollision(point_l)) or (dir_l and game.isCollision(point_u)) or (dir_r and game.isCollision(point_d))
        
        foodL = game.food[0] < game.snake.getHead()[0]
        foodR = game.food[0] > game.snake.getHead()[0]
        foodU = game.food[1] < game.snake.getHead()[1]
        foodD = game.food[1] > game.snake.getHead()[1]

        state = [
            dangerS, dangerR, dangerL,
            dir_l, dir_r, dir_u, dir_d,
            foodL, foodR, foodU, foodD
        ]

        return np.array(state, dtype=int)


    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def trainLongMemory(self):
        if len(self.memory) > BATCH_SIZE:
            miniSample = random.sample(self.memory, BATCH_SIZE)
        else:
            miniSample = self.memory
        
        for state, action, reward, next_state, done in miniSample:
            self.trainer.trainStep(state, action, reward, next_state, done)

    def trainShortMemory(self, state, action, reward, next_state, done):
        self.trainer.trainStep(state, action, reward, next_state, done)

    def getAction(self, state):
        self.epsilon = 150 - self.number_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        
        return final_move

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGame()
    while True:
        # get old state
        stateOld = agent.getState(game)

        # get action
        final_move = agent.getAction(stateOld)

        # perform action and get new state
        reward, done, score = game.game_step(final_move)
        stateNew = agent.getState(game)

        # train short memory
        agent.trainShortMemory(stateOld, final_move, reward, stateNew, done)

        # remember
        agent.remember(stateOld, final_move, reward, stateNew, done)

        if done:
            # train long memory, plot result
            game.init() # reset game

            agent.number_games += 1
            agent.trainLongMemory()

            if score > record:
                record = score
                agent.model.save()

            print("Game", agent.number_games, "Score", score, "Record:", record)

            plot_scores.append(score)
            total_score += score
            plot_mean_scores.append(total_score / agent.number_games)
            plot(plot_scores, plot_mean_scores)
            




if __name__ == "__main__":
    train()