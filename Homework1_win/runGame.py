from agent import *
import agent as ag
from game import ChineseChecker
import datetime
import tkinter as tk
from UI import GameBoard
import time

def drawTie():
    with open('ties.txt', 'a') as t:
        for row in range(1, board.board.size + 1):
            t.write(' ' * (board.board.size - row))
            for col in range(1, board.board.getColNum(row) + 1):
                str1 = str(board.board.board_status[(row, col)])
                t.write(str1 + ' ')

            t.write('\n')

        for row in range(board.board.size + 1, board.board.size * 2):
            t.write(' ' * (row - board.board.size))
            for col in range(1, board.board.getColNum(row) + 1):
                str1 = str(board.board.board_status[(row, col)])
                t.write(str1 + ' ')
            t.write('\n')

def runGame(ccgame, agents):
    state = ccgame.startState()
    print(state)
    max_iter = 200  # deal with some stuck situations
    iter = 0
    start = datetime.datetime.now()
    while (not ccgame.isEnd(state, iter)) and iter < max_iter:
        iter += 1
        board.board = state[1]
        board.draw()
        board.update_idletasks()
        board.update()

        player = ccgame.player(state)
        agent = agents[player]
        # function agent.getAction() modify class member action
        time1 = time.time()
        agent.getAction(state)
        time2 = time.time()
        if player == 1:
            print("P1's Time is :", time2 - time1)
            if (time2 - time1) > 1:
                print('\033[1;30;41m' + 'Over Time Limit' + '\033[0m')
        if player == 2:
            print("P2's Time is :", time2 - time1)
            if (time2 - time1) > 1:
                print('\033[1;30;41m' + 'Over Time Limit' + '\033[0m')
        legal_actions = ccgame.actions(state)

        if agent.action not in legal_actions:
            agent.action = random.choice(legal_actions)
        print("Sys Run Action", agent.action)
        state = ccgame.succ(state, agent.action)

    board.board = state[1]
    board.draw()
    board.update_idletasks()
    board.update()
    time.sleep(0.1)
    end = datetime.datetime.now()
    if ccgame.isEnd(state, iter):
        return state[1].isEnd(iter)[1]  # return winner
    else:  # stuck situation]
        drawTie()
        print('stuck!')
        return 0


def simulateMultipleGames(agents_dict, simulation_times, ccgame):

    steplist = []
    win_times_P1 = 0
    win_times_P2 = 0
    tie_times = 0
    utility_sum = 0
    for i in range(simulation_times):
        ag.step = 0
        run_result = runGame(ccgame, agents_dict)
        print(run_result, step)
        if run_result == 1:
            win_times_P1 += 1
        elif run_result == 2:
            win_times_P2 += 1
        elif run_result == 0:
            tie_times += 1
        steplist.append([run_result, ag.step])
        print('game', i + 1, 'finished', 'winner is player ', run_result,'\t total', ag.step,'step used')
    print('In', simulation_times, 'simulations:')
    print('winning times: for player 1 is ', win_times_P1)
    print('winning times: for player 2 is ', win_times_P2)
    print('Tie times:', tie_times)
    print('Step list', steplist)
    avg = 0
    for i in steplist:
        avg += i[1]
    print('avg step', float(avg/100))


def callback(ccgame):
    B.destroy()
    simpleGreedyAgent = SimpleGreedyAgent(ccgame)
    simpleGreedyAgent1 = SimpleGreedyAgent(ccgame)
    randomAgent = RandomAgent(ccgame)
    teamAgent = TeamNameMinimaxAgent(ccgame)
    simulateMultipleGames({1: simpleGreedyAgent, 2: teamAgent}, 1, ccgame)
    # simulateMultipleGames({1: teamAgent, 2: simpleGreedyAgent}, 1, ccgame)



if __name__ == '__main__':
    ccgame = ChineseChecker(10, 4)
    root = tk.Tk()
    board = GameBoard(root, ccgame.size, ccgame.size * 2 - 1, ccgame.board)
    board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    B = tk.Button(board, text="Start", command=lambda: callback(ccgame=ccgame))
    B.pack()
    root.mainloop()
