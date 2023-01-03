import random as rand
import time
##################
# Minimax 2D TTT #
##################

# board = [
    # [0,0,0],
    # [0,0,0],
    # [0,0,0],
# ]
# Example board, 0: empty, 1: x, -1: o
# Want an impossible to beat computer

    

class TicTacToe:
    x_o = {
        1: 'x',
        -1: 'o',
        0: '_'
    }
    def __init__(self, difficulty, human_is_x):
        self.difficulty = difficulty
        self.human_is_x = human_is_x
        self.board = [
            [0,0,0],
            [0,0,0],
            [0,0,0],
        ]
        if human_is_x:
            board_map = {
                'human': 1,
                'computer': -1
            }
        else:
            board_map = {
                'computer': 1,
                'human': -1
            }
        self.board_map = board_map
        self.winning_lines = [
            [ (x,x) for x in range(3)],
            [ (x,3-x-1) for x in range(3)],
        ]
        self.winning_lines += [[ (x,y) for x in range(3) ] for y in range(3)]
        self.winning_lines += [[ (x,y) for y in range(3) ] for x in range(3)]
    
    def print_board(self):
        print('\n'.join(['\t'.join([self.x_o[cell] for cell in row]) for row in self.board]))

    def victory_check(self):
        p1, p2 = None, None
        for line in self.winning_lines:
            values = [self.board[i][j] for i,j in line]
            if all(x == 1 for x in values):
                p1 = True, 1
            elif all(x == -1 for x in values):
                p2 = True, -1
        if p1:
            return p1
        if p2:
            return p2
        if not list(self.moves_left()):
            return True, 0
        return False, 0

    def moves_left(self):
        for i,row in enumerate(self.board):
            for j,cell in enumerate(row):
                if cell == 0:
                    yield i,j
    def minimax(self, to_max: bool, depth: int, alpha, beta):
        # self.print_board()
        game_done, winner = self.victory_check()
        if game_done:
            return -winner 
        if to_max:
            best = float('-inf')
            for i,j in self.moves_left():
                self.board[i][j] = self.board_map['computer']
                score = self.minimax(False, depth - 1, alpha, beta)
                self.board[i][j] = 0
                best = max(score, best)
                alpha = max(alpha, best)
                if alpha >= beta:
                    break
            return best
        else:
            best = float('inf')
            for i,j in self.moves_left():
                self.board[i][j] = self.board_map['human']
                score = self.minimax(True, depth - 1, alpha, beta)
                self.board[i][j] = 0
                best = min(score, best)
                beta = min(beta, best)
                if alpha >= beta:
                    break
            return best

    def human_move(self):
        coord = None
        while not isinstance(coord, int):
            try:
                coord = int(input("Enter the tile number: "))
            except:
                print("Please enter an integer.")
        i,j = coord // 3, coord % 3
        if self.board[i][j]:
            print("Tile already filled")
            self.human_move()
        else:
            self.board[i][j] = self.board_map['human']
            self.print_board()
    def computer_move(self):
        if self.difficulty == 'easy':
            coord = rand.choice(range(9))
            i,j = coord // 3, coord % 3
            if self.board[i][j]:
                self.computer_move()
            else:
                self.board[i][j] = self.board_map['computer']
                self.print_board()
        elif self.difficulty == 'very hard':
            best_score = float('-inf')
            move = None
            for i,j in self.moves_left():
                self.board[i][j] = self.board_map['computer']
                curr_score = self.minimax(False, 9, float('-inf'), float('inf'))
                # print(curr_score)
                self.board[i][j] = 0
                if curr_score > best_score:
                    move = (i,j)
                    best_score = curr_score
            self.board[move[0]][move[1]] = self.board_map['computer']
            self.print_board()
    def game_loop(self):
        self.print_board()
        if self.human_is_x:
            while True:
                game_over, winner = self.victory_check()
                if game_over:
                    print(f'Game Over! Winner is {self.x_o[winner]}')
                    break
                else:
                    self.human_move()
                    print('________________________')
                    if not list(self.moves_left()):
                        print(f'Game Over! TIE')
                        break
                    start = time.time()
                    self.computer_move()
                    end = time.time()
                    print(end-start)
        else:
            while True:
                game_over, winner = self.victory_check()
                if game_over:
                    print(f'Game Over! Winner is {self.x_o[winner]}')
                    break
                else:
                    self.computer_move()
                    print('________________________')
                    if not list(self.moves_left()):
                        print(f'Game Over! TIE')
                    self.human_move()


def main():
    TTT = TicTacToe('very hard', True)
    TTT.game_loop()


if __name__ == "__main__":
    main()
            
