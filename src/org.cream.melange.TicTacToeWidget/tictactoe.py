#!/usr/bin/env python


from random import choice

MAXDEPTH = 6

class Field(object):
    '''represents one space on the gameboard'''

    def __init__(self, line, column, content=None):
        self.line = line
        self.column = column
        self.content = content

class GameBoard(object):

    def __init__(self):
        self.field = [[Field(j, i) for i in xrange(3)] for j in xrange(3)]

    def is_full(self):
        for line in self.field:
            for field in line:
                if field.content == None:
                    return False
        return True

    def is_free(self, line, column):
        if self.field[line][column].content == None:
            return True
        else:
            return False

    def get_moves(self):
        moves = []
        for line in self.field:
            for field in line:
                if field.content == None:
                    moves.append( (field.line, field.column) )
        return moves

    def make_move(self, move, player):
        self.field[ move[0] ][ move[1] ].content = player.symbol

    def undo_move(self, move):
        self.field[ move[0] ][ move[1] ].content = None

class Player(object):

    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol

class KI(Player):
    '''An extended Playerclass with methods to calculate
       the best next game turn if maxdepth is definded with 8 or larger
    '''

    def __init__(self, name='ki', symbol='O'):
        Player.__init__(self, name, symbol)

    def calculate_move(self, game, field, player, difficulty):
        '''calculates the best move with the minimax algorithm
           which is optimized by using alpha-beta-prunning
        '''
        move = self.maximize(game, player, field, MAXDEPTH, float('-inf'), float('inf'))
        moves = [move]
        for i in xrange(difficulty):
            moves.append(choice(field.get_moves()))
        move = choice(moves)

        while not field.is_free(move[0], move[1]):
            move = choice(field.get_moves())

        field.make_move(move, self)
        return move


    def maximize(self, game, player, field, depth, alpha, beta):
        if depth == 0:
            return 0
        moves = field.get_moves()
        for move in moves:
            field.make_move(move, self)
            if game.has_won(self, field):
                value = 1
            elif depth!= 0 and game.has_won(player, field):
                value = -1
            elif field.is_full():
                value = 0
            else:
                value = self.minimize(game, player, field, depth-1, alpha, beta)

            field.undo_move(move)
            if value >= beta:
                return beta
            elif value > alpha:
                alpha = value
                if depth == MAXDEPTH:
                    best_move = move

        if depth == MAXDEPTH:
            return best_move
        else:
            return alpha


    def minimize(self, game, player, field, depth, alpha, beta):
        if depth == 0:
            return 0
        moves = field.get_moves()
        for move in moves:
            field.make_move(move, player)
            if game.has_won(player, field):
                value = -1
            elif field.is_full():
                value = 0
            else:
                value = self.maximize( game, player, field, depth-1, alpha, beta)

            field.undo_move(move)
            if depth == 0:
                return value
            if value <= alpha:
                return alpha
            if value < beta:
                beta = value

        return beta


class TicTacToe(object):

    def has_won(self, player, field):
        if self.check_horizontal(player, field):
            return True
        elif self.check_vertical(player, field):
            return True
        elif self.check_diagonal1(player, field):
            return True
        elif self.check_diagonal2(player, field):
            return True
        else:
            return False

    def check_horizontal(self, player, field):
        for line in field.field:
            count = 0
            for field in line:
                if field.content == player.symbol:
                    count += 1
                if count == 3:
                    return True
        return False

    def check_vertical(self, player, field):
        for column in xrange(3):
            count = 0
            for line in xrange(3):
                if field.field[line][column].content == player.symbol:
                    count += 1
                if count == 3:
                    return True
        return False

    def check_diagonal1(self, player, field):
        for line in xrange(3):
            for column in xrange(3):
                count = 0
                for i in xrange(line, 3):
                    if i > 2 or column > 2:
                        break
                    elif field.field[i][column].content == player.symbol:
                        count += 1
                    if count == 3:
                        return True
                    column += 1
        return False

    def check_diagonal2(self, player, field):
        for line in xrange(3):
            for column in xrange(3):
                count = 0
                for i in xrange(line, 3):
                    if i > 2 or column < 0:
                        break
                    elif field.field[i][column].content == player.symbol:
                        count += 1
                    if count == 3:
                        return True
                    column -= 1
        return False
