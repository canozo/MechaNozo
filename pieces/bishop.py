from .piece import Piece
from PIL import Image


class Bishop(Piece):
    def __init__(self, is_white, has_moved=False):
        self.is_white = is_white
        self.has_moved = has_moved
        if self.is_white:
            self.text = 'B'
            self.unicode = '\u2657'
            self.img = Image.open('pictures/bishop-w.png')
        else:
            self.text = 'b'
            self.unicode = '\u265d'
            self.img = Image.open('pictures/bishop-b.png')

    def __deepcopy__(self, memodict):
        return Bishop(self.is_white, self.has_moved)

    def can_move(self, x, y, new_x, new_y, piece_in_path):
        return abs(x-new_x) == abs(y-new_y)

    def controlled(self, table, chessboard, x, y):
        return self.possible_moves([-1, -1, 1, 1, -1], table, chessboard, x, y)
