import random
# This module will have all the code for various AI's to play t-cubed on various difficulty levels
def generate_winning_lines(board):
    n = len(board)
    winning_lines = set()
        
    # Add lines in xy plane
    winning_lines |= {tuple([(x, y, z) for y in range(n)]) for x in range(n) for z in range(n)}
    
    # Add lines in yz plane
    winning_lines |= {tuple([(x, y, z) for y in range(n)]) for z in range(n) for x in range(n)}
    
    # Add lines in zx plane
    winning_lines |= {tuple([(x, y, z) for x in range(n)]) for z in range(n) for y in range(n)}
    
    # Add lines in x direction
    winning_lines |= {tuple([(x, y, z) for x in range(n)]) for y in range(n) for z in range(n)}
    
    # Add lines in z direction
    winning_lines |= {tuple([(x, y, z) for z in range(n)]) for x in range(n) for y in range(n)}
    
    # Add diagonal lines
    winning_lines |= {tuple([(x, x, x) for x in range(n)])}
    winning_lines |= {tuple([(x, x, n-1-x) for x in range(n)])}
    winning_lines |= {tuple([(x, n-1-x, x) for x in range(n)])}
    winning_lines |= {tuple([(x, n-1-x, n-1-x) for x in range(n)])}
    winning_lines |= {tuple([(x, x, y) for x in range(n)]) for y in range(n)}
    winning_lines |= {tuple([(y, x, x) for x in range(n)]) for y in range(n)}
    winning_lines |= {tuple([(x, y, x) for x in range(n)]) for y in range(n)}
    winning_lines |= {tuple([(x, n -1 -x, y) for x in range(n)]) for y in range(n)}
    winning_lines |= {tuple([(y, x, n -1 -x) for x in range(n)]) for y in range(n)}
    winning_lines |= {tuple([(x, y, n -1 -x) for x in range(n)]) for y in range(n)}

    return winning_lines

def victory_check(board, winning_lines):
    p1, p2 = None, None
    for line in winning_lines:
        values = [board[x][y][z] for x, y, z in line]
        if all(v == 1 for v in values):
            p1 = True, 1
        elif all(v == -1 for v in values):
            p2 = True, -1
    if p1:
        return p1
    if p2:
        return p2
    if not list(get_possible_moves(board)):
        return True, 0
    return False, 0



def combine(terms):
    result = [[]]
    for term in terms:
        result = [x+[y] for x in result for y in term]
    return result

def adjacent_moves():
    return combine([[-1, 0, 1] for _ in range(3)])

def tuple_add_by_ele(a, b):
    return tuple(x + y for x,y in zip(a,b))
# IDEA 1 - Random selection
# Given an nxnxn board with game states, find an random empty tile and make a move.
def random_move(board):
    n = len(board)
    x, y, z = random.choice(range(n)), random.choice(range(n)), random.choice(range(n))
    if board[x][y][z] == 0:
        return x,y,z
    else:
        return random_move(board)

# IDEA 2: Randomly select adjacent selected tiles
# Given an nxnxn board, find all of the empty tiles adjacent to non-zero tiles and randomly choose one of those empty tiles and make a move there
def random_adjacent_move(board):
    n = len(board)
    
    # Find all non-zero tiles
    non_zero_tiles = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if board[i][j][k] == -1:
                    non_zero_tiles.append((i,j,k))

    if not non_zero_tiles:
        return random_move(board)
    # Store all empty adjacent tiles to non-zero tiles
    possible_moves = []
    for non_zero_tile in non_zero_tiles:
        # print(non_zero_tile)
        for adj in adjacent_moves():
            new_tile = tuple_add_by_ele(non_zero_tile, adj)
            # If new_tile is in range of the board, the add it to possible_moves
            try:
                i,j,k = new_tile
                if i < 0 or j < 0 or k < 0:
                    continue
                if board[i][j][k] == 0:
                    possible_moves.append(new_tile)
            except IndexError:
                continue
    # Finally, choose a random tile from possible_moves and make the move
    i,j,k = random.choice(possible_moves)

    return i,j,k

# IDEA 3: Block if about to lose and place if about to win
# Given an nxnxn board, if the opponent will win the next turn block them, if the ai will win next turn win, if not, make a move on a random adjacent tile
def random_adj_move_block(board, winning_lines):
    n = len(board)
    danger_lines, win_opp_lines = [], []
    for line in winning_lines:
        values = [board[x][y][z] for x, y, z in line]
        if values.count(1) == n - 1 and values.count(0) == 1:
            danger_lines.append(line)
        if values.count(-1) == n - 1 and values.count(0) == 1:
            win_opp_lines.append(line)
    if not win_opp_lines and not danger_lines:
        return random_adjacent_move(board)
    else:
        if win_opp_lines:
            for line in win_opp_lines:
                for i,j,k in line:
                    if board[i][j][k] == 0:
                        return i,j,k
        else:
            for line in danger_lines:
                for i,j,k in line:
                    if board[i][j][k] == 0:
                        return i,j,k

# IDEA 4: Try to fill a winning line
# Given an nxnxn board, if you are about to lose, block that tile, else try to fill a winning line
def fill_winning_lines(board, winning_lines):
    n = len(board)
    possible_lines = []
    lines = list(winning_lines)
    random.shuffle(lines)
    for line in lines:
        values = [board[x][y][z] for x, y, z in line]
        if values.count(1) == 0:
            possible_lines.append((line, values.count(-1)))
    if not possible_lines:
        return random_adj_move_block(board, winning_lines)
    danger_lines, win_opp_lines = [], []
    for line in winning_lines:
        values = [board[x][y][z] for x, y, z in line]
        if values.count(1) == n - 1 and values.count(0) == 1:
            danger_lines.append(line)
        if values.count(-1) == n - 1 and values.count(0) == 1:
            win_opp_lines.append(line)
    if danger_lines:
        for line in danger_lines:
            for i,j,k in line:
                if board[i][j][k] == 0:
                    return i,j,k
    elif win_opp_lines:
        for line in win_opp_lines:
            for i,j,k in line:
                if board[i][j][k] == 0:
                    return i,j,k
    else:
        line_to_fill, *_ = max(possible_lines, key=lambda x: x[1])
        for i,j,k in line_to_fill:
            if board[i][j][k] == 0:
                return i,j,k

# IDEA 5: Minimax
def get_almost_terminal_lines(board, winning_lines):
    n = len(board)
    danger_lines, win_opp_lines = [], []
    for line in winning_lines:
        values = [board[x][y][z] for x, y, z in line]
        if values.count(1) == n - 1 and values.count(0) == 1:
            danger_lines.append(line)
        if values.count(-1) == n - 1 and values.count(0) == 1:
            win_opp_lines.append(line)
    return danger_lines, win_opp_lines
def evaluate(board, winning_lines):
    danger_lines, win_opp_lines = get_almost_terminal_lines(board, winning_lines)
    has_won, winner = victory_check(board, winning_lines)
    if has_won:
        return winner * 10
    if winning_lines:
        return 1000
    if danger_lines:
        return -100
def get_possible_moves(board):
    n = len(board)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if board[i][j][k] == 0:
                    yield i,j,k
def best_move(board, winning_lines):
    n = len(board)
    best_score = float('-inf')
    move = (-1, -1, -1)
    if sum(1 for _ in get_possible_moves(board)) > n**3 - 5:
        return fill_winning_lines(board, winning_lines)
    for i,j,k in get_possible_moves(board):
        # print(i,j,k)
        board[i][j][k] = -1
        curr_score = minimax(board, float('-inf'), float('inf'), False, winning_lines, 0)
        board[i][j][k] = 0
        if curr_score > best_score:
            move = (i,j,k)
            best_score = curr_score
    return move

def minimax(board, alpha, beta, to_max, winning_lines, depth):
    terminal = victory_check(board, winning_lines)
    if depth == 2 or terminal[0]:
        return -terminal[1]
    if to_max:
        best = float('-inf')
        for i,j,k in get_possible_moves(board):
            board[i][j][k] = -1
            score = minimax(board, alpha, beta, False, winning_lines, depth + 1)
            board[i][j][k] = 0
            best = max(score, best)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = float('inf')
        for i,j,k in get_possible_moves(board):
            board[i][j][k] = 1
            score = minimax(board, alpha, beta, True, winning_lines, depth + 1)
            board[i][j][k] = 0
            best = min(score, best)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best
def print_nd_list(nd_list):
    print(
        "".join(["".join([str(row) + "\n" for row in depth]) + "\n" for depth in nd_list])
    )
def main():
    board = [ # We want the function to return (0, 1, 1)
        [
            [1,0,0],
            [0,0,0],
            [0,0,0],
        ],
        [
            [0,0,0],
            [0,0,0],
            [0,0,0],
        ],
        [
            [0,0,0],
            [0,0,0],
            [0,0,0],
        ],
    ]
    # print_nd_list(board)
    # board[0][1][0] = -1
    lines = generate_winning_lines(board)
    # print(len(lines))
    # print(victory_check(board, lines))
    print(best_move(board, lines))
    
        
if __name__ == "__main__":
    main()