import torch
import random
import numpy as np
from collections import deque
from snake import SnakeGame, Direction

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self) -> None:
        self.number_games = 0
        self.epsilon = 0
        self.gamma = 0
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = None
        self.trainer = None

    def getState(self, game):
        head = game.getHead()
        pL = (head[0] - game.BLOCK_SIZE, head[1])
        pR = (head[0] + game.BLOCK_SIZE, head[1])
        pU = (head[0], head[1] - game.BLOCK_SIZE)
        pD = (head[0], head[1] + game.BLOCK_SIZE)

        dirL = game.direction == Direction.LEFT
        dirR = game.direction == Direction.RIGHT
        dirU = game.direction == Direction.UP
        dirD = game.direction == Direction.DOWN

        dangerS = (dirL and game.isCollision(pL) or 
                   dirR and game.isCollision(pR) or
                   dirU and game.isCollision(pU) or
                   dirD and game.isCollision(pD))
        dangerL = (dirL and game.isCollision(pD) or 
                   dirR and game.isCollision(pU) or
                   dirU and game.isCollision(pL) or
                   dirD and game.isCollision(pR))
        dangerR = (dirL and game.isCollision(pU) or 
                   dirR and game.isCollision(pD) or
                   dirU and game.isCollision(pR) or
                   dirD and game.isCollision(pL))
        
        foodL = game.food[0] < game.head[0]
        foodR = game.food[0] > game.head[0]
        foodU = game.food[1] < game.head[0]
        foodD = game.food[1] > game.head[0]

        state = [
            dangerS, dangerR, dangerL,
            dirL, dirR, dirU, dirD,
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
        
        states, actions, rewards, next_states, dones = zip(*miniSample)
        self.trainer.trainStep(states, actions, rewards, next_states, dones)

    def trainShortMemory(self, state, action, reward, next_state, done):
        self.trainer.trainStep(state, action, reward, next_state, done)

    def getAction(self, state):
        self.epsilon = 80 - self.number_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model.predict(state)
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
                # agent.model.save()

            print("Game", agent.number_games, "Score", score, "Record:", record)

            #plot




if __name__ == "__main__":
    train()