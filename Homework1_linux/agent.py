import random, re, datetime
import copy


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
        # print("Here T")
        legal_actions = self.game.actions(state)
        
        self.action = random.choice(legal_actions)

        player = self.game.player(state)
        ### START CODE HERE ###
        board = state[1]
        
        # Define score of current state := value = 400 - sum(row_num of all P1 and P2 pieces) 
        if player == 1:
            value = 0   # 0 is smallest revenue 
            
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
                    
    def EvaluationFunction(self, state):
        value = 0
        
        end, winner = state[1].isEnd(100)
        if end:  
            if winner == 1:
                return 400  # Max revenue
            return 0        # Min revenue
        
        for player in range(1, 3):
            pos = state[1].getPlayerPiecePositions(player)
            for x, y in pos:
                value += x
        value = 400 - value
                
        return value
    
    def MinimaxAlgi(self, state, alpha, beta, current_d, max_d):
        player = state[0]
        legal_actions = self.game.actions(state)
        random.shuffle(legal_actions)
        if current_d == max_d:
            return self.EvaluationFunction(state)
        if player == 1: 
            value = 0
            for action in legal_actions:
                value = max(value, self.MinimaxAlgi(self.game.succ(state, action), 0, 400, current_d + 1 , max_d))
                if value >= beta:
                    return value
                alpha = max(alpha, value)
            return value
        
        else:
            value = 400
            for action in legal_actions:
                value = min(value, self.MinimaxAlgi(self.game.succ(state, action), 0, 400, current_d + 1, max_d))
                if value <= alpha:
                    return  value
                beta = min(beta,value)
            return value
        ### END CODE HERE ###
