from .piece import Piece
from PIL import Image


class Queen(Piece):
    def __init__(self, is_white, has_moved=False):
        self.is_white = is_white
        self.has_moved = has_moved
        if self.is_white:
            self.text = 'Q'
            self.unicode = '\u2655'
            self.img = Image.open('pictures/queen-w.png')
        else:
            self.text = 'q'
            self.unicode = '\u265b'
            self.img = Image.open('pictures/queen-b.png')

    def __deepcopy__(self, memodict):
        return Queen(self.is_white, self.has_moved)

    def can_move(self, x, y, new_x, new_y, piece_in_path):
        dx = abs(x-new_x)
        dy = abs(y-new_y)
        return dx == dy or (dx == 0 and dy != 0) or (dx != 0 and dy == 0)

    def controlled(self, table, chessboard, x, y):
        table = self.possible_moves([-1, 0, 1, 0, -1], table, chessboard, x, y)
        return self.possible_moves([-1, -1, 1, 1, -1], table, chessboard, x, y)
