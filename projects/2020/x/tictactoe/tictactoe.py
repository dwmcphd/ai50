"""
Tic Tac Toe Player
"""

import math
import random
import json

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    ?? Assumption that X always plays first
    """
    sum_X = 0
    sum_O = 0
    for i in range(0,3):
        for j in range(0,3):
            if board[i][j] == X:
                sum_X += 1
            if board[i][j] == O:
                sum_O += 1
    if sum_X==sum_O:
        return X
    return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    act_list = list()
    for i in range(0,3):
        for j in range(0,3):
            if board[i][j] == EMPTY:
                act_list.append((i,j))
    return act_list


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board=None
    if board[action[0]][action[1]]==EMPTY:
        new_board = list()
        for i in range(0, 3):
            row = list()
            for j in range(0, 3):
                if i==action[0] and j==action[1]:
                    row.append(player(board))
                else:
                    row.append(board[i][j])
            new_board.append(row)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    if player_win(X,board):
        return X
    if player_win(O,board):
        return O
    return None


def player_win(player,board):
    row = [player,player,player]
    # check row wins
    if board[0] == row or board[1] == row or board[2] == row:
        return True
    # check diag wins
    if board[0][0] == player and board[1][1] == player and board[2][2] == player:
        return True
    if board[0][2] == player and board[1][1] == player and board[2][0] == player:
        return True
    # check vertical wins
    if board[0][0] == player and board[1][0] == player and board[2][0] == player:
        return True
    if board[0][1] == player and board[1][1] == player and board[2][1] == player:
        return True
    if board[0][2] == player and board[1][2] == player and board[2][2] == player:
        return True
    return False


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if player_win(X,board):
        return True
    if player_win(O,board):
        return True
    # Doesn't quite work as semantics might imply
    #if not EMPTY in board:
    #    return True
    if not has_empty_cell(board):
        return True
    return False

def has_empty_cell(board):
    for i in range(0,3):
        for j in range(0,3):
            if not board[i][j]:
                return True
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if player_win(X,board):
        return 1
    if player_win(O,board):
        return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # find all the possible actions
    #possible_actions = actions(board)
    # For testing the other functions, just return random actions
    #action_choice = possible_actions[random.randint(0,(len(possible_actions)-1))]
    #
    #print("Starting minimax")
    state_space = get_tree(board,depth=7)
    #print(json.dumps(state_space,indent=4,sort_keys=True))

    if state_space['best_choice'] != None:
        best_choice = state_space['children'][state_space['best_choice']]
        action_choice = best_choice['action']
        print("Found a best choice")
        print_node(best_choice)
    elif state_space['children']:
        possible_actions = actions(board)
        action_choice = possible_actions[random.randint(0, (len(possible_actions) - 1))]
        print("Picking random choice")
    else:
        action_choice = state_space['action']
    print("\tReturning action:",action_choice)
    return action_choice


def get_tree(board=None,depth=1):
    """
    Recursively generates a tree of the states.
    Evaluates board states on the return of the recursion
    Depth parameter provides control over how many states are explored
    """
    node = new_node(board)
    possible_actions = actions(board)

    if depth==0:
        a = None
        #if len(possible_actions)>0:
        #    a = possible_actions[random.randint(0,(len(possible_actions)-1))]
        node['action'] = a
        #sys.exit()
        return node

    for a in possible_actions:
        new_board = result(board,a)
        # recursion here to fill out the tree
        child = get_tree(new_board, (depth - 1))
        #child = get_tree(new_board)
        child['action'] = a
        if terminal(new_board):
            child['score'] = utility(new_board)
        node['children'].append(child)

    # Some debug output to observe the recursion - Note that the "bottom" of the
    # recursion is printed first (oldest lines of text) in the output
    #print("Length node['children'] %d"%len(node['children']))
    #print("Player '%s' (Depth: %d) wants to '%s' scores"%(node['player'],depth,node['min_or_max']))
    #print("\tHas %d actions"%(len(possible_actions)),str(possible_actions))

    # Recursion above should provide a set of children that can be evaluated
    # Before returning from this level of the recursion, evaluate all of this
    # nodes children to determine which one is the 'best choice' for this node
    for i in range(0, len(node['children'])):
        child = node['children'][i]
        #print("\tChild[%d] has score: %d"%(i,child['score']))
        if node['min_or_max'] == 'max':
            # In this situation I'm looking for the best 'worst' case
            # that is assume the children (other player) will want to
            # make the best play possible
            if child['score']>node['score']:
                node['best_choice'] = i
                node['score'] = child['score']
        else:
            if child['score']<node['score']:
                node['best_choice'] = i
                node['score'] = child['score']
    #print("\tBest_Choice[%s] has score: %d"%(str(node['best_choice']), node['score']))
    return node


def new_node(board=None):
    """
    Return a dictionary that contains state
    """
    n = dict()              # record/dict for the node
    n['score'] = None       # score of the best choice
    n['action'] = None      # the (i,j) action to take
    n['best_choice'] = None # element number in the child list
    n['board'] = board
    n['children'] = list()  # list of children nodes (boards)z
    if board:
        n['player'] = player(board)
        if n['player'] == X:
            n['min_or_max'] = "max"
            n['score'] = -100  # maximizing - init to neg infinity
        else:
            n['min_or_max'] = "min"
            n['score'] = 100  # minimizing - init to pos infinity
    return n


def print_node(node):
    """
    Print text of a board with some state info
    """
    for i in range(0,3):
        print("%s\t%s\t%s"%(node['board'][i][0],node['board'][i][1],node['board'][i][2]))
    print("Score: %s\tChoice: %s\tAction: %s"%(str(node['score']),str(node['best_choice']),str(node['action'])))
    print("Children: %d"%(len(node['children'])))
    return