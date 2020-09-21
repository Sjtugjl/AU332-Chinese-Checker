# from game import ChineseChecker
# import datetime
# import tkinter as tk
# from UI import GameBoard
# import time
# import random
#
# class Agent(object):
#     def __init__(self, game):
#         self.game = game
#
#     def getAction(self, state):
#         raise Exception("Not implemented yet")
#
# class RandomAgent(Agent):
#     def getAction(self, state):
#         legal_actions = self.game.actions(state)
#         self.action = random.choice(legal_actions)
#
# ccgame = ChineseChecker(10, 4)
# ppp = RandomAgent(ccgame)
# state = ccgame.startState()
# root = tk.Tk()
# board = GameBoard(root, ccgame.size, ccgame.size * 2 - 1, ccgame.board)
# board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
# board.board = state[1]
# board.draw()
# board.update_idletasks()
# board.update()
#
# player = ccgame.player(state)
# # function agent.getAction() modify class member action
# time1 = time.time()
# ppp.getAction(state)
# time2 = time.time()
# print(type(ppp.action))

import random, re, datetime
import copy
import math


class Agent(object):
    def __init__(self, game):
        self.game = game

    def getAction(self, state):
        raise Exception("Not implemented yet")


class RandomAgent(Agent):
    def getAction(self, state):
        legal_actions = self.game.actions(state)
        self.action = random.choice(legal_actions)


class SimpleGreedyAgent(Agent):
    # a one-step-lookahead greedy agent that returns action with max vertical advance
    def getAction(self, state):
        # print("Here G")
        legal_actions = self.game.actions(state)

        self.action = random.choice(legal_actions)

        player = self.game.player(state)
        if player == 1:
            max_vertical_advance_one_step = max([action[0][0] - action[1][0] for action in legal_actions])
            max_actions = [action for action in legal_actions if
                           action[0][0] - action[1][0] == max_vertical_advance_one_step]
        else:
            max_vertical_advance_one_step = max([action[1][0] - action[0][0] for action in legal_actions])
            max_actions = [action for action in legal_actions if
                           action[1][0] - action[0][0] == max_vertical_advance_one_step]
        self.action = random.choice(max_actions)


class TeamNameMinimaxAgent(Agent):
    def get_next_actions(self, state, action):
        state = self.game.succ(state, action)
        next_actions = self.game.actions(state)
        return next_actions

    def getAction(self, state):
        global step
        # print("Here T")
        legal_actions = self.game.actions(state)

        self.action = random.choice(legal_actions)

        player = self.game.player(state)
        ### START CODE HERE ###
        board = state[1]

        # Define score of current state := value = 1000 - sum(row_num of all P1 and P2 pieces)
        if player == 1:
            value = 0  # 0 is smallest revenue
            for action in legal_actions:
                minimax_action_value = self.MinimaxAlgi(self.game.succ(state, action), 0, 400, 1, 2)
                if minimax_action_value > value:
                    value = minimax_action_value
                    self.action = action
        # else:
        #     value = 400    # 400 is greatest revenue
        #     for action in legal_actions:
        #         v = self.MinimaxAlgi(self.game.succ(state, action), 0, 400, 1, 2)
        #         if v < value:
        #             value = v
        #             self.action = action
        step += 1
        print("step:", step)

    def EvaluationFunction(self, state):
        value = 0

        end, winner = state[1].isEnd(100)
        if end:
            if winner == 1:
                return 1000  # Max revenue
            return 0  # Min revenue

        posPlayer1 = state[1].getPlayerPiecePositions1(1)
        posPlayer2 = state[1].getPlayerPiecePositions1(2)

        p1Type1Target = [[1, 1], [3, 1], [3, 3], [4, 1], [4, 2], [4, 3], [4, 4]]
        p1Type3Target = [[2, 1], [2, 2], [3, 2]]

        p2Type2Target = [[1, 1], [3, 1], [3, 3], [4, 1], [4, 2], [4, 3], [4, 4]]
        p2Type4Target = [[2, 1], [2, 2], [3, 2]]

        valueP1 = 0  # 我们的棋子的hx值
        valueP2 = 0  # 敌人的棋子的hx值
        averOfRowP1 = 0  # 我们棋子行数的平均值
        averOfRowP2 = 0  # 敌人棋子行数的平均值
        totalDiffRowP1 = 0  # 我们棋子行数与平均值的差的和
        totalDiffRowP2 = 0  # The sum of differences of the values of row of opponent's pieces and their average

        for onePiece in posPlayer1:
            averOfRowP1 += onePiece[0]
        for onePiece in posPlayer2:
            averOfRowP2 += onePiece[0]
        averOfRowP1 = averOfRowP1 / 10
        averOfRowP2 = averOfRowP2 / 10

        # Calculating the hx value of a given state of board
        for row, column, piece_type in posPlayer1:  # valueP1越小，p1越接近胜利
            if (row - 1) % 2 == 0:  # row is in odd row,hence,a middle point exists.
                left = (10 - abs(row - 10)) // 2 + 1
                valueP1 += row + 3 * math.log(abs(column - left) + 1, 5)
            else:
                left = (10 - abs(row - 10)) // 2
                right = left + 1
                valueP1 += row + 3 * math.log(min(abs(column - left), abs(column - right)) + 1, 5)
            totalDiffRowP1 += abs(row - averOfRowP1)
            if piece_type == 1 and ([row, column] in p1Type1Target):
                valueP1 -= 5
            if piece_type == 3 and ([row, column] in p1Type3Target):
                valueP1 -= 5
        valueP1 = 1000 - valueP1

        for row, column, piece_type in posPlayer2:  # valueP2越大，p2越接近胜利
            if (row - 1) % 2 == 0:  # row is in odd row,hence,a middle point exists.
                left = (10 - abs(row - 10)) // 2 + 1
                valueP2 += row + 3 * math.log(abs(column - left) + 1, 5)
            else:
                left = (10 - abs(row - 10)) // 2
                right = left + 1
                valueP2 += row + 3 * math.log(min(abs(column - left), abs(column - right)) + 1, 5)
            totalDiffRowP2 += abs(row - averOfRowP2)
            if piece_type == 2 and ([row, column] in p2Type2Target):
                valueP2 += 5
            if piece_type == 4 and ([row, column] in p2Type4Target):
                valueP2 += 5

        densityP1 = math.log(totalDiffRowP1)
        densityP2 = math.log(totalDiffRowP2)
        value = valueP1 - valueP2 - densityP1 + densityP2
        '''
        for row, y in posPlayer2:
            if (row-1)%2==0:#row is in odd row,hence,a middle point erowists.
                left = (10-abs(row-10))//2 + 1
                value += row + 3 * math.log(abs(column-left) + 1, 5)
            else:
                left = (10-abs(row-10))//2
                right = left+1
                value += row + 3* math.log(min(abs(column-left),abs(column-right))+1,5)
        '''

        return value


    def MinimaxAlgi(self, state, alpha, beta, current_d, max_d):
        player = state[0]
        legal_actions = self.game.actions(state)
        if current_d == max_d:
            return self.EvaluationFunction(state)
        legal_actions.sort(key=self.takeDepth)
        actions = legal_actions[::-1]
        actions = legal_actions
        if player == 1:
            value = 0
            for action in actions:
                value = max(value, self.MinimaxAlgi(self.game.succ(state, action), 0, 1000, current_d + 1, max_d))
                if value >= beta:
                    return value
                alpha = max(alpha, value)
            return value
        else:
            value = 1000
            for action in legal_actions:
                value = min(value, self.MinimaxAlgi(self.game.succ(state, action), 0, 1000, current_d + 1, max_d))
                if value <= alpha:
                    return value
                beta = min(beta, value)
            return value


    def takeDepth(self, action):
        return action[1][0] - action[0][0]

step = 0

        ### END CODE HERE ###
