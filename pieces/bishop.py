from .piece import Piece
from PIL import Image
from typing import List, Tuple


class Bishop(Piece):
    def __init__(self, is_white: bool, has_moved: bool=False):
        super(Bishop, self).__init__(is_white, has_moved)
        if self.is_white:
            self.img = Image.open('pictures/bishop-w.png')
        else:
            self.img = Image.open('pictures/bishop-b.png')

    def __deepcopy__(self, memodict):
        return Bishop(self.is_white, self.has_moved)

    def check_laser(self, chessboard: List[List[Piece]], x: int, y: int,
                    check_mode: bool=False) -> List[Tuple[int, int]]:
        return self.get_laser((-1, -1, 1, 1, -1), chessboard, x, y, check_mode)

    def can_move(self, x: int, y: int, new_x: int, new_y: int, piece_in_path: bool) -> bool:
        return abs(x-new_x) == abs(y-new_y)

    def controlled(self, table: List[List[bool]], chessboard: List[List[Piece]], x: int, y: int) -> List[List[bool]]:
        return self.possible_moves((-1, -1, 1, 1, -1), table, chessboard, x, y)
