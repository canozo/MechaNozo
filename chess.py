from typing import Tuple
from PIL import Image
import itertools
import os
import board


class Chess:
    def __init__(self, white: int, black: int, game_id: int, guild_id: int):
        self.white = white
        self.black = black
        self.game_id = game_id
        self.guild_id = guild_id
        self.board = board.Board()
        self.white_turn = True
        self.gameover = False
        self.old_x = 0
        self.old_y = 0
        self.new_x = 0
        self.new_y = 0

        # open images
        self.board_normal_img = Image.open('pictures/board-normal.png')
        self.board_flipped_img = Image.open('pictures/board-flipped.png')

    def get_images(self) -> Tuple[str, str]:
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
                result_normal.paste(piece_img, (x * 64, y * 64), mask=piece_img)
                result_flipped.paste(piece_img, (448 - x * 64, 448 - y * 64), mask=piece_img)

        if not os.path.isdir('temp/'):
            os.makedirs('temp/')

        result_normal.save(normal_board)
        result_flipped.save(flipped_board)
        return normal_board, flipped_board

    def move(self, player_id: int, mv_from: str, mv_into: str, promote_to: str=None) -> int:
        if (self.white_turn and player_id != self.white) or (not self.white_turn and player_id != self.black):
            # not the players turn
            return 1

        elif len(mv_from) != 2 or len(mv_into) != 2 or mv_from[0] not in 'abcdefgh' or mv_from[1] not in '12345678'\
                or mv_into[0] not in 'abcdefgh' or mv_into[1] not in '12345678':
            # wrote the move incorrectly
            return 2

        else:
            self.old_x = 'abcdefgh'.find(mv_from[0])
            self.old_y = '87654321'.find(mv_from[1])
            self.new_x = 'abcdefgh'.find(mv_into[0])
            self.new_y = '87654321'.find(mv_into[1])

            if not self.board.gatekeeper(
                    self.old_x, self.old_y, self.new_x, self.new_y, self.white_turn, False, promote_to):
                # illegal move
                return 3

            else:
                # move executed
                self.white_turn = not self.white_turn

                # checkmate happened
                if self.board.check(self.white_turn) and not self.board.has_legal_move(self.white_turn):
                    self.gameover = True

                # stalemate happened
                elif not self.board.has_legal_move(self.white_turn):
                    self.gameover = True
                return 0

    def status(self) -> Tuple[bool, bool]:
        # returns the current status of the game (is game over, is stalemate)
        return self.gameover, self.gameover and not self.board.check(self.white_turn)

    def surrender(self, player_id: int) -> int:
        winner = None

        if player_id == self.white:
            self.gameover = True
            winner = self.black

        elif player_id == self.black:
            self.gameover = True
            winner = self.white

        return winner
