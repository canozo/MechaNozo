from .piece import Piece
from PIL import Image
from typing import List, Tuple


class Queen(Piece):
    def __init__(self, is_white: bool, has_moved: bool=False):
        super(Queen, self).__init__(is_white, has_moved)
        if self.is_white:
            self.img = Image.open('pictures/queen-w.png')
        else:
            self.img = Image.open('pictures/queen-b.png')

    def __deepcopy__(self, memodict):
        return Queen(self.is_white, self.has_moved)

    def check_laser(self, chessboard: List[List[Piece]], x: int, y: int,
                    check_mode: bool=False) -> List[Tuple[int, int]]:
        laser = self.get_laser((-1, 0, 1, 0, -1), chessboard, x, y, check_mode)
        if len(laser) > 0:
            return laser
        else:
            return self.get_laser((-1, -1, 1, 1, -1), chessboard, x, y, check_mode)

    def can_move(self, x: int, y: int, new_x: int, new_y: int, piece_in_path: bool) -> bool:
        dx = abs(x-new_x)
        dy = abs(y-new_y)
        return dx == dy or (dx == 0 and dy != 0) or (dx != 0 and dy == 0)

    def controlled(self, table: List[List[bool]], chessboard: List[List[Piece]], x: int, y: int) -> List[List[bool]]:
        table = self.possible_moves((-1, 0, 1, 0, -1), table, chessboard, x, y)
        return self.possible_moves((-1, -1, 1, 1, -1), table, chessboard, x, y)
