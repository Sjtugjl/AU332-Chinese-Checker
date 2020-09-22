import random, re, datetime
import copy
import math, sys


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
    def sortkey0(self, func):
        return func[0]

    def sortkey1(self, func):
        return func[1]

    def sortdiff(self, func):
        return func[1][0] - func[0][0]

    def findTwosides(self, player, pos):
        if player == 1:
            pos.sort(key=self.sortkey0)
            firstrow = pos[0][0]
            lastrow = pos[-1][0]
        else:
            pos.sort(key=self.sortkey0)
            firstrow = pos[-1][0]
            lastrow = pos[0][0]

        return firstrow, lastrow

    ############### 开局部分评价函数值 ########################################
    def startevaluation(self, pos, target1, target3):  # 开局部分的评价函数
        valueP1 = 0  # 我们的棋子的hx值
        averOfRowP1 = 0  # 我们棋子行数的平均值
        totalDiffRowP1 = 0  # 我们棋子行数与平均值的差的和

        for onePiece in pos:
           averOfRowP1 += onePiece[0]
        averOfRowP1 = averOfRowP1 / 10

        for row, column, piece_type in pos:  # valueP1越小，p1越接近胜利
            if (row - 1) % 2 == 0:  # row is in odd row,hence,a middle point exists.
                #left = (10 - abs(row - 10)) // 2 + 1
                valueP1 += row*row #+ 3 * math.log(abs(column - left) + 1, 5)
            else:
                #left = (10 - abs(row - 10)) // 2
                #right = left + 1
                valueP1 += row*row #+ 3 * math.log(min(abs(column - left), abs(column - right)) + 1, 5)
            #totalDiffRowP1 += abs(row - averOfRowP1)
            # if piece_type == 1 and ([row, column] in target1):
            #    valueP1 -= 4
            # if piece_type == 3 and ([row, column] in target3):
            #    valueP1 -= 4

        #divergence = math.log(totalDiffRowP1, 5)
        #valueP1 -= divergence
        return -valueP1

    ############   开局部分找最大评价分 #######################################
       def maxStart(self, state, layer):
        value = min_num
        player = state[0]
        legal_actions = self.game.actions(state)
        self.action = random.choice(legal_actions)
        legal_actions.sort(key=self.sortdiff)

        posPlayer1 = state[1].getPlayerPiecePositions1(1)
        p1Type1Target = [[1, 1], [3, 1], [3, 3], [4, 1], [4, 2], [4, 3], [4, 4]]
        p1Type3Target = [[2, 1], [2, 2], [3, 2]]

        if player == 2:
            legal_actions = legal_actions[::-1]
        # start = time.time()
        # iter = 0
        for action in legal_actions:
            if action[0][0] - action[1][0] <= -1:
                continue
            if action[0][0] <= 4:
                continue
            naction = self.startevaluation(pos=posPlayer1, target1=p1Type1Target, target3=p1Type3Target)
            if value < naction:
                value = naction
        return value

    ############### 开局部总函数 ############################################
    def firstPeriod(self, state):
        global step
        player = state[0]
        legal_actions = self.game.actions(state)
        self.action = random.choice(legal_actions)
        print("random choose")
        legal_actions.sort(key=self.sortdiff)

        if player == 1:
            if step == 1:
                self.action = ((16, 1), (15, 1))
            else:
                value = min_num
                for action in legal_actions:
                    max_action_value = self.maxStart(self.game.succ(state, action), 2)
                    if max_action_value > value:
                        value = max_action_value
                        self.action = action
                        print("start one set successful.")

        return

    ############### 中期部分评价函数 #########################################
    def EvaluationFunction(self, state):

        end, winner = state[1].isEnd(100)
        if end:
            if winner == 1:
                return max_num  # Max revenue
            return min_num  # Min revenue

        posPlayer1 = state[1].getPlayerPiecePositions1(1)
        posPlayer2 = state[1].getPlayerPiecePositions1(2)

        p1Type1Target = [[1, 1], [3, 1], [3, 3], [4, 1], [4, 2], [4, 3], [4, 4]]
        p1Type3Target = [[2, 1], [2, 2], [3, 2]]

        p2Type2Target = [[19, 1], [17, 1], [17, 3], [16, 1], [16, 2], [16, 3], [16, 4]]
        p2Type4Target = [[18, 1], [18, 2], [17, 2]]

        # Calculating the hx value of a given state of board
        valueP1 = self.heuristicP1(pos=posPlayer1, target1=p1Type1Target, target3=p1Type3Target)
        valueP2 = self.heuristicP2(pos=posPlayer2, target2=p2Type2Target, target4=p2Type4Target)

        # value = valueP1 - valueP2 + densityP2
        value = valueP1 - valueP2
        return value

    def heuristicP1(self, pos, target1, target3):  # target1:p1Type1Target
        valueP1 = 0  # 我们的棋子的hx值
        averOfRowP1 = 0  # 我们棋子行数的平均值
        totalDiffRowP1 = 0  # 我们棋子行数与平均值的差的和

        for onePiece in pos:
            averOfRowP1 += onePiece[0]
        averOfRowP1 = averOfRowP1 / 10

        for row, column, piece_type in pos:  # valueP1越小，p1越接近胜利
            if (row - 1) % 2 == 0:  # row is in odd row,hence,a middle point exists.
                left = (10 - abs(row - 10)) // 2 + 1
                valueP1 += row + 3 * math.log(abs(column - left) + 1, 5)
            else:
                left = (10 - abs(row - 10)) // 2
                right = left + 1
                valueP1 += row + 3 * math.log(min(abs(column - left), abs(column - right)) + 1, 5)
            totalDiffRowP1 += abs(row - averOfRowP1)
            if piece_type == 1 and ([row, column] in target1):
                if row == 1 and column == 1:
                    valueP1 -= 7
                else:
                    valueP1 -= 4
            if piece_type == 3 and ([row, column] in target3):
                valueP1 -= 7

        #divergence = math.log(totalDiffRowP1, 4)
        #valueP1 -= divergence
        return -valueP1

    def heuristicP2(self, pos, target2, target4,base=4):
        valueP2 = 0  # 我们的棋子的hx值
        averOfRowP2 = 0  # 我们棋子行数的平均值
        totalDiffRowP2 = 0  # 我们棋子行数与平均值的差的和

        for onePiece in pos:
            averOfRowP2 += onePiece[0]
        averOfRowP2 = averOfRowP2 / 10

        for row, column, piece_type in pos:  # valueP2越大，p2越接近胜利
            if (row - 1) % 2 == 0:  # row is in odd row,hence,a middle point exists.
                left = (10 - abs(row - 10)) // 2 + 1
                valueP2 += row + 3 * math.log(abs(column - left) + 1, 5)
            else:
                left = (10 - abs(row - 10)) // 2
                right = left + 1
                valueP2 += row + 3 * math.log(min(abs(column - left), abs(column - right)) + 1, 5)
            totalDiffRowP2 += abs(row - averOfRowP2)
            if piece_type == 2 and ([row, column] in target2):
                if row == 19 and column == 1:
                    valueP2 += 7
                else:
                    valueP2 += 4
            if piece_type == 4 and ([row, column] in target4):
                valueP2 += 7

        #divergence = math.log(totalDiffRowP2, base)
        #valueP2 -= divergence
        return valueP2

    ############### 中期找最大最小评价分 ######################################
        def MinimaxAlgi(self, state, alpha, beta, current_d, max_d):
        player = state[0]
        legal_actions = self.game.actions(state)
        # if current_d == max_d:
        #     return self.EvaluationFunction(state)
        legal_actions.sort(key=self.sortdiff)
        legal_actions = legal_actions[::-1]

        if player == 1:
            value = min_num
            for action in legal_actions:
                if action[0][0] - action[1][0] <= -1:
                    continue
                if action[0][0] <= 4:
                    continue
                value = max(value,
                            self.EvaluationFunction(state))
                if value >= beta:
                    return value
                alpha = max(alpha, value)
            return value
        else:
            value = max_num
            for action in legal_actions:
                if action[0][0] - action[1][0] >= 1:
                    continue
                if action[0][0] >= 16:
                    continue
                value = min(value,
                            self.EvaluationFunction(state))
                if value <= alpha:
                    return value
                beta = min(beta, value)
            return value

    ############### 中期总函数 ##############################################
    def middlePeriod(self, state):
        global step
        player = state[0]
        value = min_num
        legal_actions = self.game.actions(state)
        self.action = random.choice(legal_actions)
        legal_actions.sort(key=self.sortdiff)
        for action in legal_actions:
            minimax_action_value = self.MinimaxAlgi(self.game.succ(state, action), min_num, max_num, 1, 2)
            if minimax_action_value > value:
                value = minimax_action_value
                self.action = action

    ############### 收官部分评价函数值 ########################################
    def lastevaluation(self, pos, target1, target3):
        valueP1 = 0  # 我们的棋子的hx值
        # averOfRowP1 = 0  # 我们棋子行数的平均值
        # totalDiffRowP1 = 0  # 我们棋子行数与平均值的差的和

        # for onePiece in pos:
        #    averOfRowP1 += onePiece[0]
        # averOfRowP1 = averOfRowP1 / 10

        for row, column, piece_type in pos:  # valueP1越小，p1越接近胜利
            #if (row - 1) % 2 == 0:  # row is in odd row,hence,a middle point exists.
            #    left = (10 - abs(row - 10)) // 2 + 1
            #    valueP1 += row + 3 * math.log(abs(column - left) + 1, 5)
            #else:
            #    left = (10 - abs(row - 10)) // 2
            #    right = left + 1
            #    valueP1 += row + 3 * math.log(min(abs(column - left), abs(column - right)) + 1, 5)
            # totalDiffRowP1 += abs(row - averOfRowP1)
            if piece_type == 1 and ([row, column] in target1):
                if row == 1 and column == 1:
                    valueP1 -= 100
                else:
                    valueP1 -= 50
            if piece_type == 3 and ([row, column] in target3):
                valueP1 -= 100
            if piece_type == 1 and ([row,column] in target3):
                valueP1 += 100
            if ([row,column] not in target1) and ([row,column] not in target3):
            #    if (row - 1) % 2 == 0:  # row is in odd row,hence,a middle point exists.
            #    left = (10 - abs(row - 10)) // 2 + 1
                valueP1 += row # + 3 * math.log(abs(column - left) + 1, 5)
            # else:
            #    left = (10 - abs(row - 10)) // 2
            #    right = left + 1
            #    valueP1 += row + 3 * math.log(min(abs(column - left), abs(column - right)) +


        # divergence = math.log(totalDiffRowP1, 5)
        # valueP1 -= divergence
        return -valueP1

    ############   收官部分找最大评价分 #######################################
    def maxEnd(self, state, layer):
        value = min_num
        player = state[0]
        legal_actions = self.game.actions(state)
        self.action = random.choice(legal_actions)
        legal_actions.sort(key=self.sortdiff)

        posPlayer1 = state[1].getPlayerPiecePositions1(1)
        posPlayer2 = state[1].getPlayerPiecePositions1(2)
        p1Type1Target = [[1, 1], [3, 1], [3, 3], [4, 1], [4, 2], [4, 3], [4, 4]]
        p1Type3Target = [[2, 1], [2, 2], [3, 2]]
        p2Type2Target = [[19, 1], [17, 1], [17, 3], [16, 1], [16, 2], [16, 3], [16, 4]]
        p2Type4Target = [[18, 1], [18, 2], [17, 2]]

        if layer == 1:
            return self.lastevaluation(pos=posPlayer1, target1=p1Type1Target, target3=p1Type3Target)
            # if player == 1:
            #     return self.heuristicP1(pos=posPlayer1, target1=p1Type1Target, target3=p1Type3Target)
            # if player == 2:
            #     return self.heuristicP2(pos=posPlayer2, target2=p2Type2Target, target4=p2Type4Target)

        if player == 2:
            legal_actions = legal_actions[::-1]

        for action in legal_actions:
            naction = self.maxEnd((player, self.game.succ(state, action)[1]), layer - 1)
            if value < naction:
                value = naction
                # self.action = action
                # print("set final act successful.")
        return value

    ############### 收官部总函数 ############################################
    def lastPeriod(self, state):
        global step
        player = state[0]
        legal_actions = self.game.actions(state)
        self.action = random.choice(legal_actions)
        legal_actions.sort(key=self.sortdiff)

        if player == 1:
            if step == 1:
                self.action = ((16, 1), (15, 1))
            else:
                value = min_num
                for action in legal_actions:
                    max_action_value = self.maxEnd(self.game.succ(state, action), 2)
                    if max_action_value > value:
                        value = max_action_value
                        self.action = action
                        print("set final successfel.")

        return

    ############### 总函数 #################################################
    def getAction(self, state):

        legal_actions = self.game.actions(state)

        self.action = random.choice(legal_actions)

        player = self.game.player(state)
        ### START CODE HERE ###
        global step
        step += 1
        board = state[1]
        pos1 = board.getPlayerPiecePositions(1)
        pos2 = board.getPlayerPiecePositions(2)
        firstrow1, lastrow1 = self.findTwosides(1, pos1)
        firstrow2, lastrow2 = self.findTwosides(2, pos2)

        if player == 1:
            value = 0  # 0 is smallest revenue
            # The Start Part of Game
            if firstrow1 >= firstrow2:
                self.firstPeriod(state)
                print("Now State", 1)
            # The Middle Part of Game
            elif firstrow1 < firstrow2 and lastrow1 >= lastrow2:
                self.middlePeriod(state)
                print("\nNow State", 2)
            # The Ending Part of Game
            elif lastrow1 < lastrow2:
                self.lastPeriod(state)
                print("Now State", 3)
            else:
                print("error in choose state of game.")

        # else:  # Play As Player 2

        print("Now step:", step)


step = 0
max_num = sys.maxsize - 1
min_num = -sys.maxsize
### END CODE HERE ###
