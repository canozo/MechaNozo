from abc import ABC, abstractmethod
from typing import List


class Piece(ABC):
    def __init__(self, is_white: bool, has_moved: bool):
        self.is_white = is_white
        self.has_moved = has_moved
        self.img = None

    @staticmethod
    def possible_moves(movements: List[int], table: List[List[bool]],
                       chessboard: List[List['Piece']], x: int, y: int) -> List[List[bool]]:
        for i in range(4):
            exit_loop = False
            sum_x = movements[i]
            sum_y = movements[i+1]
            count_x = x + sum_x
            count_y = y + sum_y

            while 0 <= count_x <= 7 and 0 <= count_y <= 7 and not exit_loop:
                exit_loop = chessboard[count_y][count_x] is not None
                table[count_y][count_x] = True
                count_x += sum_x
                count_y += sum_y
        return table

    @abstractmethod
    def can_move(self, x, y, new_x, new_y, piece_in_path):
        pass

    @abstractmethod
    def controlled(self, table, chessboard, x, y):
        pass
