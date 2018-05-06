from .piece import Piece
from PIL import Image


class Bishop(Piece):
    def __init__(self, is_white, has_moved=False):
        super(Bishop, self).__init__(is_white, has_moved)
        if self.is_white:
            self.img = Image.open('pictures/bishop-w.png')
        else:
            self.img = Image.open('pictures/bishop-b.png')

    def __deepcopy__(self, memodict):
        return Bishop(self.is_white, self.has_moved)

    def check_laser(self, chessboard, x, y, check_mode=False):
        return self.get_laser(self.diagonal, chessboard, x, y, check_mode)

    def can_move(self, x, y, new_x, new_y, piece_in_path):
        return abs(x-new_x) == abs(y-new_y)

    def controlled(self, table, chessboard, x, y):
        self.possible_moves(self.diagonal, table, chessboard, x, y)
