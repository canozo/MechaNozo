from .piece import Piece
from PIL import Image
from typing import List
import itertools


class Knight(Piece):
    def __init__(self, is_white: bool, has_moved: bool=False):
        super(Knight, self).__init__(is_white, has_moved)
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

    def can_move(self, x: int, y: int, new_x: int, new_y: int, piece_in_path: bool) -> bool:
        dx = abs(x-new_x)
        dy = abs(y-new_y)
        return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)

    def controlled(self, table: List[List[bool]], chessboard: List[List[Piece]], x: int, y: int) -> List[List[bool]]:
        for i, j in itertools.product(range(8), range(8)):
            if self.can_move(x, y, j, i, False):
                table[i][j] = True
        return table
