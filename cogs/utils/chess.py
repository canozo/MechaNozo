from PIL import Image
import itertools
import os
from time import strftime
from .board import Board


class Chess:
    def __init__(self, white, black, game_id, guild_id, guild_name, white_user,
                 black_user, white_elo, black_elo):
        self.white = white
        self.black = black
        self.game_id = game_id
        self.guild_id = guild_id
        self.guild_name = guild_name
        self.white_user = white_user
        self.black_user = black_user
        self.white_elo = white_elo
        self.black_elo = black_elo
        self.date = strftime('%Y.%m.%d')
        self.board = Board()
        self.white_turn = True
        self.white_undo = False
        self.black_undo = False
        self.white_draw = False
        self.black_draw = False
        self.gameover = False
        self.old_x = 0
        self.old_y = 0
        self.new_x = 0
        self.new_y = 0

        # open images
        self.board_normal_img = Image.open('pictures/board-normal.png')
        self.board_flipped_img = Image.open('pictures/board-flipped.png')

    def get_images(self):
        normal_board = 'temp/result-normal.png'
        flipped_board = 'temp/result-flipped.png'
        result_normal = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        result_flipped = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        result_normal.paste(self.board_normal_img, (0, 0))
        result_flipped.paste(self.board_flipped_img, (0, 0))
        chessboard = self.board.chessboard

        for y, x in itertools.product(range(8), repeat=2):
            if chessboard[y][x] is not None:
                piece_img = chessboard[y][x].img
                result_normal.paste(
                    piece_img, (x * 64, y * 64), mask=piece_img)
                result_flipped.paste(
                    piece_img, (448 - x * 64, 448 - y * 64), mask=piece_img)

        if not os.path.isdir('temp/'):
            os.makedirs('temp/')

        result_normal.save(normal_board)
        result_flipped.save(flipped_board)
        return normal_board, flipped_board

    def move(self, player_id, mv_from, mv_into, promote_to=None):
        if (self.white_turn and player_id != self.white) or \
                (not self.white_turn and player_id != self.black):
            # not the players turn
            return 1

        elif len(mv_from) != 2 \
                or len(mv_into) != 2 \
                or mv_from[0] not in 'abcdefgh' \
                or mv_from[1] not in '12345678' \
                or mv_into[0] not in 'abcdefgh' \
                or mv_into[1] not in '12345678':
            # wrote the move incorrectly
            return 2

        else:
            self.old_x = 'abcdefgh'.find(mv_from[0])
            self.old_y = '87654321'.find(mv_from[1])
            self.new_x = 'abcdefgh'.find(mv_into[0])
            self.new_y = '87654321'.find(mv_into[1])

            if not self.board.gatekeeper(self.old_x,
                                         self.old_y,
                                         self.new_x,
                                         self.new_y,
                                         False,
                                         promote_to):
                # illegal move
                return 3

            else:
                # move executed
                self.white_undo = False
                self.black_undo = False
                self.white_turn = self.board.white_turn

                # checkmate happened
                if self.board.is_checked and not self.board.has_moves:
                    self.gameover = True

                # stalemate happened
                elif not self.board.has_moves:
                    self.gameover = True
                return 0

    def status(self):
        # returns the current status of the game (is game over, is stalemate)
        return self.gameover, self.gameover and not self.board.is_checked

    def surrender(self, player_id):
        if player_id == self.white:
            self.board.surrender(True)
            self.gameover = True
            winner = self.black
        else:
            self.board.surrender(False)
            self.gameover = True
            winner = self.white
        return winner

    def draw(self, player_id):
        if player_id == self.white:
            self.white_draw = True
        elif player_id == self.black:
            self.black_draw = True

        if self.white_draw and self.black_draw:
            self.white_draw = self.black_draw = False
            self.board.draw()
            self.gameover = True
            return True
        else:
            return False

    def takeback(self, player_id):
        if player_id == self.white:
            self.white_undo = True
        elif player_id == self.black:
            self.black_undo = True

        if self.white_undo and self.black_undo:
            self.white_undo = self.black_undo = False
            self.board.undo()
            self.white_turn = self.board.white_turn
            return True
        else:
            return False

    def get_pgn(self):
        tags = '[Event "Discord Chess game"]\n'\
               f'[Site "{self.guild_name}"]\n'\
               f'[Date "{self.date}"]\n'\
               '[Round "-"]\n'\
               f'[White "{self.white_user}"]\n'\
               f'[Black "{self.black_user}"]\n'\
               f'[Result "{self.board.result}"]\n'\
               f'[WhiteElo "{self.white_elo}"]\n'\
               f'[BlackElo "{self.black_elo}"]\n'\
               '[Variant "Standard"]\n\n'
        return tags + self.board.pgn
