from .piece import Piece
from PIL import Image


class Queen(Piece):
    def __init__(self, is_white, has_moved=False):
        super(Queen, self).__init__(is_white, has_moved)
        if self.is_white:
            self.img = Image.open('pictures/queen-w.png')
        else:
            self.img = Image.open('pictures/queen-b.png')

    def __deepcopy__(self, memodict):
        return Queen(self.is_white, self.has_moved)

    def check_laser(self, chessboard, x, y, check_mode=False):

        laser = self.get_laser(self.straight, chessboard, x, y, check_mode)
        if len(laser) > 0:
            return laser
        else:
            return self.get_laser(self.diagonal, chessboard, x, y, check_mode)

    def can_move(self, x, y, new_x, new_y, piece_in_path):
        dx = abs(x-new_x)
        dy = abs(y-new_y)
        return dx == dy or (dx == 0 and dy != 0) or (dx != 0 and dy == 0)

    def controlled(self, table, chessboard, x, y):
        table = self.possible_moves(self.straight, table, chessboard, x, y)
        return self.possible_moves(self.diagonal, table, chessboard, x, y)
