from .piece import Piece
from PIL import Image


class King(Piece):
    def __init__(self, is_white, has_moved=False):
        self.is_white = is_white
        self.has_moved = has_moved
        if self.is_white:
            self.text = 'K'
            self.unicode = '\u2654'
            self.img = Image.open('pictures/king-w.png')
        else:
            self.text = 'k'
            self.unicode = '\u265a'
            self.img = Image.open('pictures/king-b.png')

    def __deepcopy__(self, memodict):
        return King(self.is_white, self.has_moved)

    def can_move(self, x, y, new_x, new_y, piece_in_path):
        dx = abs(x-new_x)
        dy = abs(y-new_y)
        return (dx == dy == 1) or (dx == 0 and dy == 1) or (dx == 1 and dy == 0)

    def controlled(self, table, chessboard, x, y):
        for i in range(8):
            for j in range(8):
                if self.can_move(x, y, j, i, False):
                    table[i][j] = True
        return table
