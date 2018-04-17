from abc import ABC, abstractmethod
from typing import List, Tuple


class Piece(ABC):
    def __init__(self, is_white: bool, has_moved: bool):
        self.is_white = is_white
        self.has_moved = has_moved
        self.img = None

    def get_laser(self, movements: Tuple[int, ...], chessboard: List[List['Piece']],
                  x: int, y: int, check_mode: bool) -> List[Tuple[int, int]]:
        from .king import King
        for i in range(4):
            piece_count = 0
            laser = [(y, x)]
            sum_x = movements[i]
            sum_y = movements[i+1]
            count_x = x + sum_x
            count_y = y + sum_y

            while 0 <= count_x <= 7 and 0 <= count_y <= 7:
                piece = chessboard[count_y][count_x]
                if piece is not None:
                    if piece.is_white == self.is_white:
                        break
                    elif check_mode and isinstance(piece, King) and piece_count == 0:
                        return laser
                    elif check_mode:
                        break
                    elif isinstance(piece, King) and piece_count == 1:
                        return laser
                    else:
                        piece_count += 1
                laser.append((count_y, count_x))
                count_x += sum_x
                count_y += sum_y
        return []

    @staticmethod
    def possible_moves(movements: Tuple[int, ...], table: List[List[bool]],
                       chessboard: List[List['Piece']], x: int, y: int) -> List[List[bool]]:
        from .king import King
        for i in range(4):
            exit_loop = False
            sum_x = movements[i]
            sum_y = movements[i+1]
            count_x = x + sum_x
            count_y = y + sum_y

            while 0 <= count_x <= 7 and 0 <= count_y <= 7 and not exit_loop:
                piece = chessboard[count_y][count_x]
                exit_loop = piece is not None and not isinstance(piece, King)
                table[count_y][count_x] = True
                count_x += sum_x
                count_y += sum_y
        return table

    @abstractmethod
    def check_laser(self, chessboard, x, y, check_mode):
        pass

    @abstractmethod
    def can_move(self, x, y, new_x, new_y, piece_in_path):
        pass

    @abstractmethod
    def controlled(self, table, chessboard, x, y):
        pass
