from .piece import Piece
from PIL import Image
from typing import List


class Pawn(Piece):
    def __init__(self, is_white: bool, has_moved: bool=False):
        super(Pawn, self).__init__(is_white, has_moved)
        if self.is_white:
            self.text = 'P'
            self.unicode = '\u2659'
            self.img = Image.open('pictures/pawn-w.png')
        else:
            self.text = 'p'
            self.unicode = '\u265f'
            self.img = Image.open('pictures/pawn-b.png')

    def __deepcopy__(self, memodict):
        return Pawn(self.is_white, self.has_moved)

    def can_move(self, x: int, y: int, new_x: int, new_y: int, piece_in_path: bool) -> bool:
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

    def controlled(self, table: List[List[bool]], chessboard: List[List[Piece]], x: int, y: int) -> List[List[bool]]:
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
