from .piece import Piece
from PIL import Image
import itertools


class Knight(Piece):
    def __init__(self, is_white, has_moved=False):
        super(Knight, self).__init__(is_white, has_moved)
        if self.is_white:
            self.img = Image.open('pictures/knight-w.png')
        else:
            self.img = Image.open('pictures/knight-b.png')

    def __deepcopy__(self, memodict):
        return Knight(self.is_white, self.has_moved)

    def check_laser(self, chessboard, x, y, check_mode):
        return []

    def can_move(self, x, y, new_x, new_y, piece_in_path):
        dx = abs(x-new_x)
        dy = abs(y-new_y)
        return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)

    def controlled(self, table, chessboard, x, y):
        for i, j in itertools.product(range(8), repeat=2):
            if self.can_move(x, y, j, i, False):
                table[i][j] = True
        return table
