from .piece import Piece
from PIL import Image


class Pawn(Piece):
    def __init__(self, is_white, has_moved=False):
        super(Pawn, self).__init__(is_white, has_moved)
        if self.is_white:
            self.img = Image.open('pictures/pawn-w.png')
        else:
            self.img = Image.open('pictures/pawn-b.png')

    def __deepcopy__(self, memodict):
        return Pawn(self.is_white, self.has_moved)

    def check_laser(self, chessboard, x, y, check_mode):
        return []

    def can_move(self, x, y, new_x, new_y, piece_in_path):
        dx = abs(x-new_x)
        dy = y-new_y

        if not self.is_white:
            dy = -dy

        if dx == 0 and dy == 1 and not piece_in_path:
            return True
        elif dx == 1 and dy == 1 and piece_in_path:
            return True
        elif dx == 0 and dy == 2 and not piece_in_path and not self.has_moved:
            return True

        return False

    def controlled(self, table, chessboard, x, y):
        if (self.is_white and y == 0) or (not self.is_white and y == 7):
            return table

        if self.is_white:
            dy = y-1
        else:
            dy = y+1

        if x < 7:
            table[dy][x+1] = True
        if x > 0:
            table[dy][x-1] = True

        return table
