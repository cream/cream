#!/usr/bin/env python

from cream.contrib.melange import api

from time import sleep

from tictactoe import Player
from tictactoe import GameBoard
from tictactoe import KI
from tictactoe import TicTacToe as Game


@api.register('tictactoe')
class TicTacToe(api.API):

    def __init__(self):

        api.API.__init__(self)

        self.tictactoe = Game()
        self.game_board = GameBoard()
        self.player = Player('player', 'X')
        self.computer = KI('computer', 'O')
        self.game_over = False

    @api.expose
    def player_turn(self, line, column):
        if not self.game_over:
            self.game_board.make_move((int(line), int(column)), self.player)
            self.set_game_over()

    @api.expose
    def computer_turn(self, difficulty):
        #add some thrill
        sleep(0.4)

        if not self.game_over:
            line, column = self.computer.calculate_move(self.tictactoe,
                                                        self.game_board,
                                                        self.player,
                                                        int(difficulty)
            )
            self.set_game_over()
            return str(line) + '|' + str(column)

    @api.expose
    def reset(self):
        self.game_board = GameBoard()
        self.game_over = False

    @api.expose
    def move_allowed(self, line, column):
        return self.game_board.is_free(int(line), int(column)) and not self.game_over

    def set_game_over(self):
        if self.tictactoe.has_won(self.player, self.game_board):
            self.game_over = True
        elif self.tictactoe.has_won(self.computer, self.game_board):
            self.game_over = True
        elif self.game_board.is_full():
            self.game_over = True
