from typing import TypeVar, List
from pieces.piece import Piece
from pieces.rook import Rook
from pieces.bishop import Bishop
from pieces.knight import Knight
from pieces.queen import Queen
from pieces.king import King
from pieces.pawn import Pawn
import itertools
import copy

T = TypeVar('T', Piece, None)


class Board:
    def __init__(self):
        # game settings
        self.en_passant_x = -1
        self.en_passant_y = -1
        self.promotion = False
        self.en_passant = False
        self.promote_to = None
        self.white_controlled = None  # type: List[List[bool]]
        self.black_controlled = None  # type: List[List[bool]]
        self.chessboard = [[None for _ in range(8)] for _ in range(8)]  # type: List[List[T]]

        # initial position
        self.chessboard[0][0] = Rook(False)
        self.chessboard[0][1] = Knight(False)
        self.chessboard[0][2] = Bishop(False)
        self.chessboard[0][3] = Queen(False)
        self.chessboard[0][4] = King(False)
        self.chessboard[0][5] = Bishop(False)
        self.chessboard[0][6] = Knight(False)
        self.chessboard[0][7] = Rook(False)

        self.chessboard[1][0] = Pawn(False)
        self.chessboard[1][1] = Pawn(False)
        self.chessboard[1][2] = Pawn(False)
        self.chessboard[1][3] = Pawn(False)
        self.chessboard[1][4] = Pawn(False)
        self.chessboard[1][5] = Pawn(False)
        self.chessboard[1][6] = Pawn(False)
        self.chessboard[1][7] = Pawn(False)

        self.chessboard[7][0] = Rook(True)
        self.chessboard[7][1] = Knight(True)
        self.chessboard[7][2] = Bishop(True)
        self.chessboard[7][3] = Queen(True)
        self.chessboard[7][4] = King(True)
        self.chessboard[7][5] = Bishop(True)
        self.chessboard[7][6] = Knight(True)
        self.chessboard[7][7] = Rook(True)

        self.chessboard[6][0] = Pawn(True)
        self.chessboard[6][1] = Pawn(True)
        self.chessboard[6][2] = Pawn(True)
        self.chessboard[6][3] = Pawn(True)
        self.chessboard[6][4] = Pawn(True)
        self.chessboard[6][5] = Pawn(True)
        self.chessboard[6][6] = Pawn(True)
        self.chessboard[6][7] = Pawn(True)

        # iniial controlled squares
        self.update_controlled()

    def gatekeeper(
            self, x: int, y: int, nx: int, ny: int, white_turn: bool, review_mode: bool, promote_to: str=None) -> bool:
        legal = True
        flag_ep = False

        # check that a piece was selected
        if self.chessboard[y][x] is None:
            legal = False
        else:
            # piece selected was of the players color
            if white_turn != self.chessboard[y][x].is_white:
                legal = False

            # no friendly fire
            if legal and self.chessboard[ny][nx] and white_turn == self.chessboard[ny][nx].is_white:
                legal = False

            # check if player wants to castle
            if legal and isinstance(self.chessboard[y][x], King) and not self.check(white_turn) and abs(x-nx) == 2:
                legal = legal and self.can_castle(x, y, nx, ny)

            # check if can do en passant
            elif legal and self.en_passant and isinstance(self.chessboard[y][x], Pawn)\
                    and nx == self.en_passant_x and ny == self.en_passant_y:
                legal = self.chessboard[y][x].can_move(x, y, nx, ny, True)

            #  all normal moves
            elif legal and not self.chessboard[y][x].can_move(x, y, nx, ny, self.chessboard[ny][nx] is not None):
                legal = False

            # check that there's no jumping pieces
            if legal and not isinstance(self.chessboard[y][x], Knight) and not isinstance(self.chessboard[y][x], King):
                legal = legal and not self.jumps(x, y, nx, ny)

            # check white king doesn't move to a controlled square
            if legal and isinstance(self.chessboard[y][x], King) and white_turn and self.black_controlled[ny][nx]:
                legal = False

            # check black king doesn't move to a controlled square
            elif legal and isinstance(self.chessboard[y][x], King) and not white_turn and self.white_controlled[ny][nx]:
                legal = False

            # check that king doesn't move to a square that was covered by himself
            if legal and isinstance(self.chessboard[y][x], King) and self.is_pinned(x, y, nx, ny, white_turn, True):
                legal = False

            # check that we're not moving pinned pieces
            elif legal and not isinstance(self.chessboard[y][x], King)\
                    and self.is_pinned(x, y, nx, ny, white_turn, False):
                legal = False

            # check if the player can promote
            if legal and isinstance(self.chessboard[y][x], Pawn)\
                    and ((white_turn and ny == 0) or (not white_turn and ny == 7)):
                legal = self.can_promote(promote_to)

            # get ready for a possible en passant on next turn
            if legal and isinstance(self.chessboard[y][x], Pawn) and abs(y-ny) == 2:
                flag_ep = True
                self.en_passant_x = x
                if white_turn and self.black_controlled[y+1][x]:
                    self.en_passant_y = y-1
                elif not white_turn and self.white_controlled[y-1][x]:
                    self.en_passant_y = y+1

        if not review_mode and legal:
            self.execute(x, y, nx, ny, white_turn)

            if self.en_passant:
                self.en_passant = False

            if flag_ep:
                self.en_passant = True

        return legal

    def execute(self, x: int, y: int, nx: int, ny: int, white_turn: bool) -> None:
        if isinstance(self.chessboard[y][x], King):
            if nx-x == 2:
                self.chessboard[y][nx-1] = self.chessboard[y][nx+1]
                self.chessboard[y][nx+1] = None

            elif nx-x == -2:
                self.chessboard[y][nx+1] = self.chessboard[y][nx-2]
                self.chessboard[y][nx-2] = None

        if self.en_passant and isinstance(self.chessboard[y][x], Pawn)\
                and ny == self.en_passant_y and nx == self.en_passant_x:
            if white_turn:
                self.chessboard[ny+1][nx] = None
            else:
                self.chessboard[ny-1][nx] = None

        if self.promotion:
            if self.promote_to == 'queen':
                self.chessboard[ny][nx] = Queen(white_turn)

            elif self.promote_to == 'knight':
                self.chessboard[ny][nx] = Knight(white_turn)

            elif self.promote_to == 'bishop':
                self.chessboard[ny][nx] = Bishop(white_turn)

            elif self.promote_to == 'rook':
                self.chessboard[ny][nx] = Rook(white_turn)

            self.promotion = False
        else:
            self.chessboard[y][x].has_moved = True
            self.chessboard[ny][nx] = self.chessboard[y][x]

        self.chessboard[y][x] = None
        self.update_controlled()

    def can_castle(self, x: int, y: int, nx: int, ny: int) -> bool:
        dx = nx - x
        dy = ny - y

        if dy:
            return False

        if dx > 0:
            rook_x = nx + 1
            increment = 1
        else:
            rook_x = nx - 2
            increment = -1

        if self.chessboard[y][rook_x].has_moved or self.chessboard[y][x].has_moved:
            return False

        if self.chessboard[y][rook_x] is None:
            return False

        if self.jumps(x, y, rook_x, ny):
            return False

        i = x
        while i != nx + increment:
            if self.chessboard[y][x].is_white and self.black_controlled[y][i]:
                return False
            elif not self.chessboard[y][x].is_white and self.white_controlled[y][i]:
                return False
            i += increment

        return True

    def is_pinned(self, x: int, y: int, nx: int, ny: int, white_turn: bool, king_mode: bool) -> bool:
        king_y = king_x = 0
        temp_chessboard = copy.deepcopy(self.chessboard)

        for i, j in itertools.product(range(8), repeat=2):
            if self.chessboard[i][j] is not None and isinstance(self.chessboard[i][j], King)\
                    and self.chessboard[i][j].is_white == white_turn:
                king_x = j
                king_y = i

        temp_chessboard[ny][nx] = temp_chessboard[y][x]
        temp_chessboard[y][x] = None
        temp_controlled = [[False for _ in range(8)] for _ in range(8)]

        for i, j in itertools.product(range(8), repeat=2):
            if temp_chessboard[i][j] is not None and temp_chessboard[i][j].is_white != white_turn:
                temp_controlled = temp_chessboard[i][j].controlled(temp_controlled, temp_chessboard, j, i)

        if king_mode:
            return temp_controlled[ny][nx]
        else:
            return temp_controlled[king_y][king_x]

    def jumps(self, x: int, y: int, nx: int, ny: int) -> bool:
        dx = abs(x-nx)
        dy = abs(y-ny)

        # check vertically
        if not dx:
            if ny-y < 0:
                increment = -1
            else:
                increment = 1

            i = y + increment
            while i != ny:
                if self.chessboard[i][nx] is not None:
                    return True
                i += increment

        # check horizontally
        elif not dy:
            if nx-x < 0:
                increment = -1
            else:
                increment = 1

            i = x + increment
            while i != nx:
                if self.chessboard[ny][i] is not None:
                    return True
                i += increment

        # check diagonally
        elif dx == dy:
            if nx-x < 0:
                increment_x = -1
            else:
                increment_x = 1

            if ny-y < 0:
                increment_y = -1
            else:
                increment_y = 1

            ix = x + increment_x
            iy = y + increment_y
            while ix != nx and iy != ny:
                if self.chessboard[iy][ix] is not None:
                    return True
                ix += increment_x
                iy += increment_y

        return False

    def update_controlled(self) -> None:
        self.white_controlled = [[False for _ in range(8)] for _ in range(8)]
        self.black_controlled = [[False for _ in range(8)] for _ in range(8)]
        for i, j in itertools.product(range(8), repeat=2):
            if self.chessboard[i][j] is not None and self.chessboard[i][j].is_white:
                self.white_controlled = self.chessboard[i][j].controlled(self.white_controlled, self.chessboard, j, i)
            elif self.chessboard[i][j] is not None and not self.chessboard[i][j].is_white:
                self.black_controlled = self.chessboard[i][j].controlled(self.black_controlled, self.chessboard, j, i)

    def can_promote(self, promote_to: str) -> bool:
        if promote_to is None:
            return False
        elif promote_to not in ('queen', 'knight', 'bishop', 'rook'):
            return False
        else:
            self.promotion = True
            self.promote_to = promote_to
            return True

    def check(self, white_turn: bool) -> bool:
        king_y = king_x = 0
        for i, j in itertools.product(range(8), repeat=2):
            if self.chessboard[i][j] and isinstance(self.chessboard[i][j], King)\
                    and self.chessboard[i][j].is_white == white_turn:
                king_x = j
                king_y = i

        if white_turn:
            return self.black_controlled[king_y][king_x]
        else:
            return self.white_controlled[king_y][king_x]

    def has_legal_move(self, white_turn: bool) -> bool:
        for i, j, k, l in itertools.product(range(8), repeat=4):
            if self.gatekeeper(j, i, l, k, white_turn, True, 'queen'):
                return True

        return False
