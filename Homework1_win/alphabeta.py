for action in legal_actions:
    if action == preaction:
        continue
    if action[0][0] - action[1][0] <= -1:
        continue
    if action[0][0] <= 4:
        continue
    minimax_action_value = self.MinimaxAlgiP1(self.game.succ(state, action), min_num, max_num, 1, 2)
    if minimax_action_value > value:
        value = minimax_action_value
        bestAction = action