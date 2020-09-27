import random, re, datetime



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


class lookThreeSteps(Agent):
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

    def isDivChange(self, pos, firstrow, lastrow, player):
        if player == 1:
            if pos[0] < firstrow:
                return True
            elif pos[0] > lastrow:
                return True
        else:
            if pos[0] > firstrow:
                return True
            elif pos[0] < lastrow:
                return True
        return False

    ############### 开局部分评价函数值 ########################################
    def startevaluation(self, pos, target1, target3):  # 开局部分的评价函数
        valueP1 = 0  # 我们的棋子的hx值
        divergence = 0
        #averOfRowP1 = 0  # 我们棋子行数的平均值
        #totalDiffRowP1 = 0  # 我们棋子行数与平均值的差的和
        firstRow = 19
        lastRow = 0

        #for onePiece in pos:
        #   averOfRowP1 += onePiece[0]
        #averOfRowP1 = averOfRowP1 / 10

        for row, column, piece_type in pos:# valueP1越小，p1越接近胜利
            if row < firstRow:
                firstRow = row
            if row > lastRow:
                lastRow = row
            if (row - 1) % 2 == 0:  # row is in odd row,hence,a middle point exists.
                left = (10 - abs(row - 10)) // 2 + 1
                valueP1 += row + 3 * math.log(abs(column - left) + 1, 5)
            else:
                left = (10 - abs(row - 10)) // 2
                right = left + 1
                valueP1 += row + 3 * math.log(min(abs(column - left), abs(column - right)) + 1, 5)
            #totalDiffRowP1 += abs(row - averOfRowP1)
            # if piece_type == 1 and ([row, column] in target1):
            #    valueP1 -= 4
            # if piece_type == 3 and ([row, column] in target3):
            #    valueP1 -= 4

        if lastRow - firstRow > 9:
            divergence = 5

        valueP1 += divergence

        return -valueP1
    def getActionEvaluation(self, action, firstrow, lastrow, player):
        p1Type1Target = [[1, 1], [3, 1], [3, 3], [4, 1], [4, 2], [4, 3], [4, 4]]
        p1Type3Target = [[2, 1], [2, 2], [3, 2]]
        p2Type2Target = [[19, 1], [17, 1], [17, 3], [16, 1], [16, 2], [16, 3], [16, 4]]
        p2Type4Target = [[18, 1], [18, 2], [17, 2]]
          # 我们的棋子的hx值
        valueP1 = [0, 0]
        divergence = 0
        i = 0
        for pos in action:
            valueP1[i] = 0
            row = pos[0]
            column = pos[1]
            if (row - 1) % 2 == 0:  # row is in odd row,hence,a middle point exists.
                left = (10 - abs(row - 10)) // 2 + 1
                valueP1[i] += row + 3 * math.log(abs(column - left) + 1, 5)
            else:
                left = (10 - abs(row - 10)) // 2
                right = left + 1
                valueP1[i] += row + 3 * math.log(min(abs(column - left), abs(column - right)) + 1, 5)
            i += 1
        # finalValueP1 = valueP1[0] - valueP1[1] # 对 P1 final 越大越好
        pos = action[1]

        if self.isDivChange(pos, firstrow, lastrow, player):
            lastRow0 = lastrow
            firstRow0 = firstrow
            if player == 1: # 更新fir las
                if pos[0] < firstrow:
                    firstrow = pos[0]
                elif pos[0] > lastrow:
                    lastrow = pos[0]
            else:
                if pos[0] > firstrow:
                    firstrow = pos[0]
                elif pos[0] < lastrow:
                    lastrow = pos[0]
            if lastrow - firstrow > 9 and lastRow0 - firstRow0 < 9:
                divergence = -9
            elif lastrow - firstrow < 9 and lastRow0 - firstRow0 > 9:
                divergence = 9
            else:
                divergence = 0
        else:
            divergence = 0
        valueP1[0] = -valueP1[0]
        valueP1[1] = -valueP1[1]
        finalValueP1 = -valueP1[0] + valueP1[1]
        finalValueP1 += divergence
        return finalValueP1, firstrow, lastrow

    ############   开局部分找最大评价分 #######################################
    def maxStart(self, state, basicvalue, firstrow, lastrow, level, max): # P1 ok, P2 ok value现在都是越大越好
        global preaction
        player = state[0]
        legal_actions = self.game.actions(state)
        self.action = random.choice(legal_actions)
        legal_actions.sort(key=self.sortdiff)
        level = level + 1
        value = 0
        orivalue = basicvalue

        if player == 2:
            legal_actions = legal_actions[::-1]

        if player == 1:
            value = min_num
            if level == max:
                legal_actions = legal_actions[:5]
            else:
                legal_actions = legal_actions[:5]

            for action in legal_actions:
                if action == preaction:
                    continue
                if action == preaction[::-1]:
                    continue
                if action[0][0] - action[1][0] <= -1:
                    continue
                if action[0][0] <= 4:
                    continue
                board = copy.deepcopy(state[1])
                board.board_status[action[1]] = board.board_status[action[0]]
                board.board_status[action[0]] = 0
                next_state = (player, board)
                dx, firstrow, lastrow = self.getActionEvaluation(action, firstrow, lastrow, player)
                basicvalue = orivalue + dx
                if level == max:
                    # print('value', basicvalue, 'dx', dx, 'action',action)
                    if value < basicvalue:
                        value = basicvalue
                else:
                    max_action_value = self.maxStart(next_state, basicvalue, firstrow, lastrow, level, max)
                    if value < max_action_value:
                        value = max_action_value
        else:
            pass
            # value = min_num
            # legal_actions = legal_actions[:40]
            # for action in legal_actions:
            #     if action == preaction:
            #         continue
            #     if action == preaction[::-1]:
            #         continue
            #     if action[0][0] - action[1][0] >= 1:
            #         continue
            #     if action[0][0] >= 16:
            #         continue
            #     board = copy.deepcopy(state[1])
            #     board.board_status[action[1]] = board.board_status[action[0]]
            #     board.board_status[action[0]] = 0
            #     next_state = (player, board)
            #     posPlayer = next_state[1].getPlayerPiecePositions1(player)
            #     naction = self.startevaluation(pos=posPlayer, target1=p2Type2Target, target3=p2Type4Target)
            #     if value < naction:
            #         value = naction
        return value

    ############### 开局部总函数 ############################################
    def firstPeriod(self, state):# P1 ok, P2 no OK    value都是得到最大值
        global step, preaction
        player = state[0]
        legal_actions = self.game.actions(state)
        tmp = random.choice(legal_actions)
        rdm = tmp
        legal_actions.sort(key=self.sortdiff)
        firstrow, lastrow = 0, 0
        posPlayer1 = state[1].getPlayerPiecePositions1(1)
        p1Type1Target = [[1, 1], [3, 1], [3, 3], [4, 1], [4, 2], [4, 3], [4, 4]]
        p1Type3Target = [[2, 1], [2, 2], [3, 2]]

        posPlayer2 = state[1].getPlayerPiecePositions1(2)
        p2Type2Target = [[19, 1], [17, 1], [17, 3], [16, 1], [16, 2], [16, 3], [16, 4]]
        p2Type4Target = [[18, 1], [18, 2], [17, 2]]

        if player == 1:
            firstrow, lastrow = self.findTwosides(player, posPlayer1)
            basicvalue = self.startevaluation(posPlayer1, target1=p1Type1Target, target3=p1Type3Target)
            # print('baas',basicvalue)
        else:
            firstrow, lastrow = self.findTwosides(player, posPlayer2)
            basicvalue = self.startevaluation(posPlayer2, target1=p2Type2Target, target3=p2Type4Target)

        if player == 1:
            if step == 1:
                tmp = ((16, 1), (15, 2))
                preaction = ((16, 1), (15, 2))
            else:
                value = min_num
                bestValue = min_num
                actionlist = []
                bestAction = None

                orivalue = basicvalue
                legal_actions = legal_actions[:15]
                for action in legal_actions:
                    if action == preaction:
                        continue
                    if action[0][0] - action[1][0] <= -1:
                        continue

                    board = copy.deepcopy(state[1])
                    board.board_status[action[1]] = board.board_status[action[0]]
                    board.board_status[action[0]] = 0
                    next_state = (player, board)
                    dx, firstrow, lastrow = self.getActionEvaluation(action, firstrow, lastrow, player)
                    # print('dx', dx, 'action', action)
                    basicvalue = orivalue + dx
                    max_action_value = self.maxStart(next_state, basicvalue, firstrow, lastrow, 1, 3)
                    if max_action_value > value:
                        value = max_action_value
                        tmp = action
                        preaction = tmp[::-1]
                # print('action', tmp)

################  尝试算三步，但是目前每走一步要5s左右   ########################
                # for action in legal_actions:
                #     if action[0][0] - action[1][0] <= -1:
                #         continue
                #     state = self.game.succ(state, action)
                #     legal_actions1 = self.game.actions(state)
                #     legal_actions1.sort(key=self.sortdiff)
                #
                #     for action1 in legal_actions1:
                #         if action1[0][0] - action1[1][0] <= -1:
                #             continue
                #         max_action_value = self.maxStart(self.game.succ(state, action), 2)
                #         if max_action_value > value:
                #             value = max_action_value
                #
                #     max_action1_value = value
                #     if max_action1_value > bestValue:
                #         bestValue = max_action1_value
                #         tmp = action
                #         print("action",tmp)

        # if rdm == tmp:
        #     print('\033[1;30;41m' + 'No action to use but random' + '\033[0m')
        elif player == 2:
            pass
            # if step == 1:
            #     tmp = ((4, 1), (5, 2))
            # else:
            #     value = min_num
            #     bestValue = min_num
            #     actionlist = []
            #     bestAction = None
            #
            #     for action in legal_actions:
            #         if action == preaction:
            #             continue
            #         if action[0][0] - action[1][0] >= 1:
            #             continue
            #         board = copy.deepcopy(state[1])
            #         board.board_status[action[1]] = board.board_status[action[0]]
            #         board.board_status[action[0]] = 0
            #         next_state = (player, board)
            #         max_action_value = self.maxStart(next_state, basicvalue, firstrow, lastrow, 1, 3)
            #         if max_action_value > value:
            #             value = max_action_value
            #             tmp = action
            #             preaction = tmp[::-1]
        return tmp

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
        firstRow = 19
        lastRow = 0
        divergence = 0

        for row, column, piece_type in pos:  # valueP1越小，p1越接近胜利
            if row < firstRow:
                firstRow = row
            if row > lastRow:
                lastRow = row
            if (row - 1) % 2 == 0:  # row is in odd row,hence,a middle point exists.
                left = (10 - abs(row - 10)) // 2 + 1
                valueP1 += row + 3 * math.log(abs(column - left) + 1, 5)
            else:
                left = (10 - abs(row - 10)) // 2
                right = left + 1
                valueP1 += row + 3 * math.log(min(abs(column - left), abs(column - right)) + 1, 5)
            if piece_type == 1 and ([row, column] in target1):
                if row == 1 and column == 1:
                    valueP1 -= 12
                else:
                    valueP1 -= 4 * row
            if piece_type == 3 and ([row, column] in target3):
                valueP1 -= 7
            if piece_type == 3 and row == 1 and column == 1:
                valueP1 += 100000

        if lastRow - firstRow > 7:
            divergence = 9

        valueP1 += divergence
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


    def getActionEvaluationMid(self, action, firstrow, lastrow, piece_type, player):

        target1 = [[1, 1], [3, 1], [3, 3], [4, 1], [4, 2], [4, 3], [4, 4]]
        target3 = [[2, 1], [2, 2], [3, 2]]

        target2 = [[19, 1], [17, 1], [17, 3], [16, 1], [16, 2], [16, 3], [16, 4]]
        target4 = [[18, 1], [18, 2], [17, 2]]
          # 我们的棋子的hx值
        if player == 1:
            # print("p1", action)
            valueP1 = [0, 0]
            divergence = 0
            i = 0
            for pos in action:  # valueP1越小，p1越接近胜利
                valueP1[i] = 0
                row = pos[0]
                column = pos[1]
                if (row - 1) % 2 == 0:  # row is in odd row,hence,a middle point exists.
                    left = (10 - abs(row - 10)) // 2 + 1
                    valueP1[i] += row + 3 * math.log(abs(column - left) + 1, 5)
                else:
                    left = (10 - abs(row - 10)) // 2
                    right = left + 1
                    valueP1[i] += row + 3 * math.log(min(abs(column - left), abs(column - right)) + 1, 5)
                if piece_type == 1 and ([row, column] in target1):
                    if row == 1 and column == 1:
                        valueP1[i] -= 12
                    else:
                        valueP1[i] -= 4 * row
                if piece_type == 3 and ([row, column] in target3):
                    valueP1[i] -= 7
                if piece_type == 3 and row == 1 and column == 1:
                    valueP1[i] += 100000
                i += 1
            pos = action[1]

            if self.isDivChange(pos, firstrow, lastrow, player):
                lastRow0 = lastrow
                firstRow0 = firstrow
                if player == 1: # 更新fir las
                    if pos[0] < firstrow:
                        firstrow = pos[0]
                    elif pos[0] > lastrow:
                        lastrow = pos[0]
                else:
                    if pos[0] > firstrow:
                        firstrow = pos[0]
                    elif pos[0] < lastrow:
                        lastrow = pos[0]
                if lastrow - firstrow > 7 and lastRow0 - firstRow0 < 7:
                    divergence = 9
                elif lastrow - firstrow < 7 and lastRow0 - firstRow0 > 7:
                    divergence = -9
                else:
                    divergence = 0
            else:
                divergence = 0
            valueP1[0] = -valueP1[0]
            valueP1[1] = -valueP1[1]
            finalValueP1 = -valueP1[0] + valueP1[1]
            finalValueP1 -= divergence
            return finalValueP1, firstrow, lastrow
        else: # P2
            # print("p2", action)
            i = 0
            valueP2 = [0, 0]
            for pos in action:  # valueP2越大，p2越接近胜利
                valueP2[i] = 0
                row = pos[0]
                column = pos[1]
                if (row - 1) % 2 == 0:  # row is in odd row,hence,a middle point exists.
                    left = (10 - abs(row - 10)) // 2 + 1
                    valueP2[i] += row + 3 * math.log(abs(column - left) + 1, 5)
                else:
                    left = (10 - abs(row - 10)) // 2
                    right = left + 1
                    valueP2[i] += row + 3 * math.log(min(abs(column - left), abs(column - right)) + 1, 5)
                if piece_type == 2 and ([row, column] in target2):
                    if row == 19 and column == 1:
                        valueP2[i] += 7
                    else:
                        valueP2[i] += 4
                if piece_type == 4 and ([row, column] in target4):
                    valueP2[i] += 7
            pos = action[1]

            # if self.isDivChange(pos, firstrow, lastrow, player):
            #     lastRow0 = lastrow
            #     firstRow0 = firstrow
            #     if player == 1:  # 更新fir las
            #         if pos[0] < firstrow:
            #             firstrow = pos[0]
            #         elif pos[0] > lastrow:
            #             lastrow = pos[0]
            #     else:
            #         if pos[0] > firstrow:
            #             firstrow = pos[0]
            #         elif pos[0] < lastrow:
            #             lastrow = pos[0]
            #     if lastrow - firstrow > 9 and lastRow0 - firstRow0 < 9:
            #         divergence = -9
            #     elif lastrow - firstrow < 9 and lastRow0 - firstRow0 > 9:
            #         divergence = 9
            #     else:
            #         divergence = 0
            # else:
            #     divergence = 0
            # valueP2[0] = -valueP2[0]
            # valueP2[1] = -valueP2[1]
            finalvalueP2 = -valueP2[0] + valueP2[1]
            # finalvalueP2 += divergence
            return finalvalueP2, firstrow, lastrow

    ############### 中期找最大最小评价分 ######################################
    def maxMidP1(self, state, basicvalue, alpha, beta, firstrow, lastrow, level, max):#P1 ok
        global preaction
        player = state[0]
        legal_actions = self.game.actions(state)
        legal_actions.sort(key=self.sortdiff)
        level = level + 1
        value = 0

        orivalue = basicvalue
        if player == 2:
            legal_actions = legal_actions[::-1]
            legal_actions = legal_actions[:40]

        if player == 1:
            value = min_num
            if level == max:
                legal_actions = legal_actions[:20]
            else:
                legal_actions = legal_actions[:20]

            for action in legal_actions:
                if action == preaction:
                    continue
                if action == preaction[::-1]:
                    continue
                if action[0][0] - action[1][0] <= -1:
                    continue
                if action[0][0] <= 4:
                    continue
                succor = self.game.succ(state, action)
                piece_type = succor[1].board_status[action[1]]
                dx, firstrow, lastrow = self.getActionEvaluationMid(action, firstrow, lastrow, piece_type, player)
                basicvalue = orivalue + dx
                po = self.EvaluationFunction(succor)

                if level == max:
                    # print("Here2")
                    # print('value', basicvalue, 'dx', dx, 'ori', orivalue, 'po', po, 'action',action)
                    if value < basicvalue:
                        value = basicvalue
                else:
                    basicvalue = self.maxMidP1(succor,basicvalue, alpha,beta, firstrow,lastrow,level,max)
                    value = max(value, basicvalue)
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
                succor = self.game.succ(state, action)
                piece_type = succor[1].board_status[action[1]]
                dx, firstrow, lastrow = self.getActionEvaluationMid(action, firstrow, lastrow, piece_type, player)
                basicvalue = orivalue + dx
                if level == max:
                    # print('value', basicvalue, 'dx', dx, 'action', action)
                    if value > basicvalue:
                        value = basicvalue
                else:
                    # print("Here1")
                    basicvalue = self.maxMidP1(succor, basicvalue, alpha, beta, firstrow, lastrow, level, max)
                    value = min(value, basicvalue)
                    if value <= alpha:
                        return value
                    beta = min(beta, value)
            return value

    # def MinimaxAlgiP2(self, state, alpha, beta, current_d, max_d):  # P2 ok
    #     global preaction
    #     player = state[0]
    #     legal_actions = self.game.actions(state)
    #     legal_actions.sort(key=self.sortdiff)
    #
    #     if player == 2:
    #         legal_actions = legal_actions[::-1]
    #         legal_actions = legal_actions[:40]
    #         value = min_num
    #         for action in legal_actions:
    #             if action == preaction:
    #                 continue
    #             if action[0][0] - action[1][0] >= 1:
    #                 continue
    #             if action[0][0] >= 16:
    #                 continue
    #             succor = self.game.succ(state, action)
    #             value = max(value,
    #                         self.EvaluationFunction(succor))
    #             if value >= beta:
    #                 return value
    #             alpha = max(alpha, value)
    #         return value
    #     else:
    #         legal_actions = legal_actions[:40]
    #         value = max_num
    #         for action in legal_actions:
    #             if action[0][0] - action[1][0] <= -1:
    #                 continue
    #             if action[0][0] <= 4:
    #                 continue
    #             value = min(value,
    #                         self.EvaluationFunction(state))
    #             if value <= alpha:
    #                 return value
    #             beta = min(beta, value)
    #         return value

    ############### 中期总函数 ##############################################
    def middlePeriod(self, state):  #P1 ok . P2 OK value big is good
        alpha = max_num
        beta = min_num
        global step, preaction
        player = state[0]
        value = min_num
        legal_actions = self.game.actions(state)
        tmp = random.choice(legal_actions)
        rdm = tmp
        legal_actions.sort(key=self.sortdiff)
        firstrow1, lastrow1 = 0, 0
        posPlayer1 = state[1].getPlayerPiecePositions1(1)
        p1Type1Target = [[1, 1], [3, 1], [3, 3], [4, 1], [4, 2], [4, 3], [4, 4]]
        p1Type3Target = [[2, 1], [2, 2], [3, 2]]

        posPlayer2 = state[1].getPlayerPiecePositions1(2)
        p2Type2Target = [[19, 1], [17, 1], [17, 3], [16, 1], [16, 2], [16, 3], [16, 4]]
        p2Type4Target = [[18, 1], [18, 2], [17, 2]]

        if player == 1:
            firstrow1, lastrow1 = self.findTwosides(player, posPlayer1)
            basicvalue = self.EvaluationFunction(state)
            # print('baas',basicvalue)
        else:
            firstrow2, lastrow2 = self.findTwosides(player, posPlayer2)
            basicvalue = self.EvaluationFunction(state)
            # print("Base", basicvalue)

        if player == 2:
            legal_actions = legal_actions[::-1]
            legal_actions = legal_actions[:40]
        if player == 1:
            legal_actions = legal_actions[:40]
            orivalue = basicvalue
            # print("Base", orivalue)
            for action in legal_actions:
                if action == preaction:
                    continue
                if action[0][0] - action[1][0] <= -1:
                    continue
                if action[0][0] <= 4:
                    continue
                succor = self.game.succ(state, action)
                player = state[0]
                # print("Player", player)  Player 1
                piece_type = succor[1].board_status[action[1]]

                dx, firstrow1, lastrow1 = self.getActionEvaluationMid(action, firstrow1, lastrow1, piece_type, player)

                basicvalue = orivalue + dx
                po = self.EvaluationFunction(succor)
                # print("eva", po, 'bas' , basicvalue, 'dx', dx, action)
                minimax_action_value = self.maxMidP1(succor, basicvalue, alpha, beta, firstrow1, lastrow1, 1, 3)
                if minimax_action_value > value:
                    value = minimax_action_value
                    tmp = action
                    preaction = tmp[::-1]
        else:
            pass
            # for action in legal_actions:
            #     if action == preaction:
            #         continue
            #     if action[0][0] - action[1][0] >= 1:
            #         continue
            #     if action[0][0] >= 16 :
            #         continue
            #     minimax_action_value = self.MinimaxAlgiP2(self.game.succ(state, action), min_num, max_num, 1, 2)
            #     if minimax_action_value > value:
            #         value = minimax_action_value
            #         tmp = action
            #         preaction = tmp[::-1]
#       if rdm == tmp:
#            print('\033[1;30;41m' + 'No action to use but random' + '\033[0m')
        return tmp

    ############### 收官部分评价函数值 ########################################
    def lastevaluation(self, pos, target1, target3):
        valueP1 = 0  # 我们的棋子的hx值
        positionScore = 0 #The basic score based on the sum of rows of my our pieces
        targetScore = [0] #The bonus or penalty of a going to a target,


        for row, column, piece_type in pos:  # valueP1越小，p1越接近胜利
            if piece_type == 1 and ([row, column] in target1):
                if row == 1 and column == 1:
                    targetScore[0] += 1000
                    targetScore.append([row,column,"Blue in Peak"])
                else:
                    targetScore[0] += 50
                    targetScore.append([row,column,"Blue in BLue"])
            if piece_type == 3 and ([row, column] in target3):
                targetScore[0] += 1000
                targetScore.append([row,column,"Yellow in Yellow"])

            if piece_type == 1 and ([row,column] in target3):
                targetScore[0] -= 100
                targetScore.append([row,column,"Blue in Yellow"])
            if piece_type == 3 and row==1 and column ==1:
                targetScore[0] -= 100000
                targetScore.append([row,column,"Yellow in Peak"])
            if ([row,column] not in target1) and ([row,column] not in target3):
                positionScore += row # + 3 * math.log(abs(column - left) + 1, 5)

        valueP1 = valueP1 - positionScore + targetScore[0]
        return valueP1
    def getActionEvaluationEnd(self, action, player, piece):
        target1 = [[1, 1], [3, 1], [3, 3], [4, 1], [4, 2], [4, 3], [4, 4]]
        target3 = [[2, 1], [2, 2], [3, 2]]
        p2Type2Target = [[19, 1], [17, 1], [17, 3], [16, 1], [16, 2], [16, 3], [16, 4]]
        p2Type4Target = [[18, 1], [18, 2], [17, 2]]
        valueP1 = [0, 0]  # 我们的棋子的hx值
        positionScore = [0, 0]  # The basic score based on the sum of rows of my our pieces
        finalValueP1 = 0
        i = 0
        for pos in action:  # valueP1越小，p1越接近胜利

            valueP1[i] = 0
            row = pos[0]
            column = pos[1]
            piece_type = piece
            if piece_type == 1 and ([row, column] in target1):
                if row == 1 and column == 1:
                    valueP1[i] += 1000
                else:
                    valueP1[i] += 50
            if piece_type == 3 and ([row, column] in target3):
                valueP1[i] += 1000

            if piece_type == 1 and ([row, column] in target3):
                valueP1[i] -= 100
            if piece_type == 3 and row == 1 and column == 1:
                valueP1[i] -= 100000
            if ([row, column] not in target1) and ([row, column] not in target3):
                positionScore[i] += row  # + 3 * math.log(abs(column - left) + 1, 5)
            i += 1
        valueP1[0] = valueP1[0] - positionScore[0]
        valueP1[1] = valueP1[1] - positionScore[1]
        finalValueP1 = -valueP1[0] + valueP1[1]
        return finalValueP1
    # finalValueP1 = valueP1[0] - valueP1[1] # 对 P1 final 越大越好
    ############   收官部分找最大评价分 #######################################
    def maxEnd(self, state, basicvalue, level, max): # P1  ok, p2 OK value big is good
        global preaction, step
        value = min_num
        legal_actions = self.game.actions(state)
        self.action = random.choice(legal_actions)
        legal_actions.sort(key=self.sortdiff)
        player = state[0]
        level = level + 1
        orivalue = basicvalue

        p1Type1Target = [[1, 1], [3, 1], [3, 3], [4, 1], [4, 2], [4, 3], [4, 4]]
        p1Type3Target = [[2, 1], [2, 2], [3, 2]]
        p2Type2Target = [[19, 1], [17, 1], [17, 3], [16, 1], [16, 2], [16, 3], [16, 4]]
        p2Type4Target = [[18, 1], [18, 2], [17, 2]]

        if player == 2:
            legal_actions = legal_actions[::-1]
            legal_actions  = legal_actions[:40]

        if state[1].isEnd(step)[0]:
            value = max_num
        else:
            if player == 1 :
                if level == max:
                    legal_actions = legal_actions[:3]
                else:
                    legal_actions = legal_actions[:5]

                for action in legal_actions:
                    if action == preaction:
                        continue
                    if action == preaction[::-1]:
                        continue
                    board = copy.deepcopy(state[1])
                    board.board_status[action[1]] = board.board_status[action[0]]
                    board.board_status[action[0]] = 0
                    next_state = (player, board)
                    piece_type = board.board_status[action[1]]
                    posI = board.getPlayerPiecePositions1(player)
                    eva = self.lastevaluation(posI, p1Type1Target, p1Type3Target)
                    dx = self.getActionEvaluationEnd(action, player, piece_type)
                    basicvalue = orivalue + dx
                    if basicvalue == 3300:
                        value = basicvalue
                        break
                    # print('ori', orivalue, 'dx', dx, 'bas', basicvalue, 'eva', eva)
                    if level == max:
                        if value < basicvalue:
                            value = basicvalue
                    else:
                        max_action_value = self.maxEnd(next_state, basicvalue, level, max)
                        if value < max_action_value:
                            value = max_action_value
            else:
                pass
                # legal_actions = legal_actions[:40]
                # for action in legal_actions:
                #     if action == preaction:
                #         continue
                #     if action == preaction[::-1]:
                #         continue
                #     board = copy.deepcopy(state[1])
                #     board.board_status[action[1]] = board.board_status[action[0]]
                #     board.board_status[action[0]] = 0
                #     next_state = (player, board)
                #     posPlayer = next_state[1].getPlayerPiecePositions1(player)
                #     naction, positionScore, targetScore = self.lastevaluation(pos=posPlayer, target1=p2Type2Target, target3=p2Type4Target)
                #     if value < naction:
                #         value = naction
                #         bestpositionScore = positionScore
                #         besttargetScore = targetScore
        return value

    ############### 收官部总函数 ############################################
    def lastPeriod(self, state): # P1 ok, P2 OK value big is good
        global preaction
        global step
        player = state[0]
        oriboard = state[1]
        legal_actions = self.game.actions(state)
        tmp = random.choice(legal_actions)
        rdm = tmp
        legal_actions.sort(key=self.sortdiff)
        bestList = []
        posPlayer1 = state[1].getPlayerPiecePositions1(1)
        p1Type1Target = [[1, 1], [3, 1], [3, 3], [4, 1], [4, 2], [4, 3], [4, 4]]
        p1Type3Target = [[2, 1], [2, 2], [3, 2]]
        posPlayer2 = state[1].getPlayerPiecePositions1(2)
        p2Type2Target = [[19, 1], [17, 1], [17, 3], [16, 1], [16, 2], [16, 3], [16, 4]]
        p2Type4Target = [[18, 1], [18, 2], [17, 2]]
        if player == 1:
            basicvalue = self.lastevaluation(posPlayer1, target1=p1Type1Target, target3=p1Type3Target)
            # print('baas',basicvalue)
        else:
            basicvalue = self.lastevaluation(posPlayer2, target1=p2Type2Target, target3=p2Type4Target)
        if player == 1:
            value = min_num
            legal_actions = legal_actions[:20]
            orivalue = basicvalue
            for action in legal_actions:
                if action == preaction:
                    continue

                board = copy.deepcopy(state[1])
                board.board_status[action[1]] = board.board_status[action[0]]
                board.board_status[action[0]] = 0
                next_state = (player, board)
                piece_type = board.board_status[action[1]]

                dx = self.getActionEvaluationEnd(action, player, piece_type)
                # print('dx', dx, 'action', action)
                basicvalue = orivalue + dx
                if basicvalue == 3300:
                    tmp = action
                    break
                max_action_value= self.maxEnd(next_state, basicvalue,1 ,3)
                if max_action_value > value:
                    bestList = []
                    bestList.append(action)
                    value = max_action_value
                elif max_action_value == value:
                    bestList.append(action)
            tmp = random.choice(bestList)
            print("bestlist", bestList)
            print("tmp",tmp)
            preaction = tmp[::-1]
        else:
            value = min_num
            legal_actions   = legal_actions[::-1]
            for action in legal_actions:
                if action == preaction:
                    continue
                board = copy.deepcopy(state[1])
                board.board_status[action[1]] = board.board_status[action[0]]
                board.board_status[action[0]] = 0
                next_state = (player, board)
                max_action_value, positionScore, targetScore = self.maxEnd(next_state, action)
                # print("action:", action, ",value:", max_action_value)
                # print("basic score:", positionScore)
                # print("target score:", targetScore)
                if max_action_value > value:
                    bestList = []
                    bestList.append(action)
                    value = max_action_value
                elif max_action_value == value:
                    bestList.append(action)
            tmp = random.choice(bestList)
            print("bestlist", bestList)
            print("tmp", tmp)
            preaction = tmp[::-1]
     #   if rdm == tmp:
     #       print('\033[1;30;41m' + 'No action to use but random' + '\033[0m')
        return tmp

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

        # The Start Part of Game
        if firstrow1 >= firstrow2:
            tmp = self.firstPeriod(state)
            self.action = tmp
            print("Now State", 1, "action:", self.action)
        # The Middle Part of Game
        elif firstrow1 < firstrow2  and lastrow1 >= lastrow2 :
            tmp = self.middlePeriod(state)
            self.action = tmp
            print("\nNow State", 2, 'action', self.action)
        # The Ending Part of Game
        elif lastrow1 < lastrow2:
            tmp = self.lastPeriod(state)
            self.action = tmp
            print("\nNow State", 3, 'Final Action', self.action)
        else:
            print('\033[1;30;41m' + 'error in choose state of game.' + '\033[0m')
        print("Now step:", step, "Want Run", self.action)

import sys, copy, math
step = 0
preaction = None
max_num = sys.maxsize - 1
min_num = -sys.maxsize
### END CODE HERE ###
