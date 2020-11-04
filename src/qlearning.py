#!/usr/bin/python3

import sys
import constant
from enum import Enum
from random import randint, random

class State:
    def __init__(self, coord : tuple, currentW):
        self.coord = coord
        self.currentW = currentW
    def __eq__(self, other):
        return other != None and self.coord[0] == other.coord[0] and self.coord[1] == other.coord[1]\
            and self.currentW == other.currentW
    def __lt__(self, other):
        return self.coord[0] < other.coord[0] and self.coord[1] < other.coord[1] \
            and self.currentW < other.currentW
    def __hash__(self):
        return hash((self.coord, self.currentW))
    def __str__(self) -> str:
        return "({}, {}, {})".format(self.coord[0], self.coord[1], self.currentW)

class Action(Enum):
    DOWN = (lambda coord: (coord[0]+1,coord[1]),)
    RIGHT = (lambda coord: (coord[0],coord[1]+1),)
    UP = (lambda coord: (coord[0]-1,coord[1]),)
    LEFT = (lambda coord: (coord[0],coord[1]-1),)

    def __call__(self, *args, **kwargs):
        return self.value[0](*args, **kwargs)

class Reward(Enum):
    FREEPLACE = -1
    LOCALIZATION_POINT = 1
    OBSTACLE = -10
    NOT_IN_WORD = -10
    COLLECT_POINT = 10

inputFilename = sys.argv[1]
learnRate = float(sys.argv[2])
explorationStrategyFactor = float(sys.argv[3])
discountFactor = float(sys.argv[4])
iterations = int(sys.argv[5])

inputFile = open(inputFilename, 'r')
y, x, w = [int(i) for i in next(inputFile).split()]
industryMap = [[i for i in line.rstrip('\n')] for line in inputFile]

qTable = dict()

def initializeQ():
    for i in range(y):
        for j in range(x):
            for currentW in range(w+1):
                qTable[State((i, j), currentW)] = {action:0 for action in Action}

def firstState():
    line = randint(0, y - 1)
    column = randint(0, x - 1)
    while industryMap[line][column] in constant.TERMINALS:
        line = randint(0, y - 1)
        column = randint(0, x - 1)
    
    return State((line, column), w)

def getOptimalAction(currentState : State) -> Action:
    return max(qTable[currentState], key=qTable[currentState].get)

def actionGenerator(state : State) -> Action:
    if state != None and random() >= explorationStrategyFactor:
        return getOptimalAction(state)
    
    index = randint(0, len(Action) - 1)
    return list(Action)[index]

def getNextState(currentState: State, action : Action) -> tuple:
    coordNextState = action(currentState.coord)
    reward = Reward.NOT_IN_WORD.value
    if coordNextState[0] < 0 or coordNextState[0] >= y \
        or coordNextState[1] < 0 or coordNextState[1] >= x:

        return (currentState, reward)
    
    cell = industryMap[coordNextState[0]][coordNextState[1]]
    nextW = currentState.currentW-1
    if cell == constant.COLLECT_POINT:
        reward = Reward.COLLECT_POINT
    elif cell == constant.FREEPLACE:
        reward = Reward.FREEPLACE
    elif cell == constant.LOCALIZATION_POINT:
        reward = Reward.LOCALIZATION_POINT
        nextW = w
    elif cell == constant.OBSTACLE:
        reward = Reward.OBSTACLE
    else:
        assert(False)

    return (State(coordNextState, nextW), reward.value)

def updateQTable(action : Action, reward : int, currentState : State, oldState : State, \
    alpha, gamma):

    oldValue = qTable[oldState][action]
    maxQ = qTable[oldState][max(qTable[oldState], key=qTable[oldState].get)]

    newValue = oldValue + alpha * (reward + gamma * maxQ - oldValue)

    qTable[oldState][action] = newValue

def qLearning():
    initializeQ()
    for _ in range(iterations):
        currentState = firstState()
        action = actionGenerator(None)

        while industryMap[currentState.coord[0]][currentState.coord[1]] in constant.NONTERMINALS and \
            (currentState.currentW >= 0 or \
                industryMap[currentState.coord[0]][currentState.coord[1]] == constant.LOCALIZATION_POINT):

            nextState, reward = getNextState(currentState, action)

            if nextState.currentW < 0:
                break

            updateQTable(action, reward, nextState, currentState, learnRate, discountFactor)

            action = actionGenerator(nextState)
            currentState = nextState

def savePiFile():
    piFile = open("pi.txt", "w")
    assert(piFile)

    for state, actionsReward in qTable.items():
        if industryMap[state.coord[0]][state.coord[1]] == constant.OBSTACLE:
            continue

        for action, reward in actionsReward.items():
            if reward != 0.0:
                piFile.write("{} {}, {:.2f}\n".format(state, action.name, reward))

qLearning()
savePiFile()