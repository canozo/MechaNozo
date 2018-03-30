from .piece import Piece
from PIL import Image


class Knight(Piece):
    def __init__(self, is_white, has_moved=False):
        self.is_white = is_white
        self.has_moved = has_moved
        if self.is_white:
            self.text = 'N'
            self.unicode = '\u2658'
            self.img = Image.open('pictures/knight-w.png')
        else:
            self.text = 'n'
            self.unicode = '\u265e'
            self.img = Image.open('pictures/knight-b.png')

    def __deepcopy__(self, memodict):
        return Knight(self.is_white, self.has_moved)

    def can_move(self, x, y, new_x, new_y, piece_in_path):
        dx = abs(x-new_x)
        dy = abs(y-new_y)
        return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)

    def controlled(self, table, chessboard, x, y):
        for i in range(8):
            for j in range(8):
                if self.can_move(x, y, j, i, False):
                    table[i][j] = True
        return table
