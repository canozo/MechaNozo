import copy
import itertools
from PIL import Image
from typing import Tuple, List
from pieces.rook import Rook
from pieces.bishop import Bishop
from pieces.knight import Knight
from pieces.queen import Queen
from pieces.king import King
from pieces.pawn import Pawn


class Board:
    def __init__(self):
        # game settings
        self.en_passant_x = -1
        self.en_passant_y = -1
        self.promotion = False
        self.promote_to = None
        self.en_passant = False
        self.white_controlled = None
        self.black_controlled = None
        self.chessboard = [[None for _ in range(8)] for _ in range(8)]  # type: List[...]

        # open images
        self.board_normal_img = Image.open('pictures/board-normal.png')
        self.board_flipped_img = Image.open('pictures/board-flipped.png')

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

        # initiate controlled squares
        self.update_controlled()

    def gatekeeper(self, old_x, old_y, new_x, new_y, white_turn, review_mode, promote_to=None) -> bool:
        legal = True
        flag_ep = False

        # check that a piece was selected
        if self.chessboard[old_y][old_x] is None:
            legal = False
        else:
            # piece selected was of the players color
            if white_turn != self.chessboard[old_y][old_x].is_white:
                legal = False

            # no friendly fire
            if self.chessboard[new_y][new_x] and white_turn == self.chessboard[new_y][new_x].is_white:
                legal = False

            # check if player wants to castle
            if isinstance(self.chessboard[old_y][old_x], King) and not self.check(white_turn) and abs(old_x-new_x) == 2:
                legal = legal and self.castle(old_x, old_y, new_x, new_y)

            # check if can do en passant
            elif self.en_passant and isinstance(self.chessboard[old_y][old_x], Pawn)\
                    and new_x == self.en_passant_x and new_y == self.en_passant_y:
                legal = self.chessboard[old_y][old_x].can_move(old_x, old_y, new_x, new_y, True)

            #  all normal moves
            elif not self.chessboard[old_y][old_x].can_move(
                    old_x, old_y, new_x, new_y, self.chessboard[new_y][new_x] is not None):
                legal = False

            # check that there's no jumping pieces
            if not isinstance(self.chessboard[old_y][old_x], Knight)\
                    and not isinstance(self.chessboard[old_y][old_x], King):
                legal = legal and not self.jumps(old_x, old_y, new_x, new_y)

            # check white king doesn't move to a controlled square
            if isinstance(self.chessboard[old_y][old_x], King) and white_turn and self.black_controlled[new_y][new_x]:
                legal = False

            # check black king doesn't move to a controlled square
            elif isinstance(self.chessboard[old_y][old_x], King) and not white_turn\
                    and self.white_controlled[new_y][new_x]:
                legal = False

            # check that king doesn't move to a square that was covered by himself
            if legal and isinstance(self.chessboard[old_y][old_x], King)\
                    and self.pin(old_x, old_y, new_x, new_y, white_turn, True):
                legal = False

            # check that we're not moving pinned pieces
            elif legal and not isinstance(self.chessboard[old_y][old_x], King)\
                    and self.pin(old_x, old_y, new_x, new_y, white_turn, False):
                legal = False

            # check if the player can promote
            if legal and isinstance(self.chessboard[old_y][old_x], Pawn)\
                    and ((white_turn and new_y == 0) or (not white_turn and new_y == 7)):
                legal = self.can_promote(promote_to)

            # get ready for a possible en passant on next turn
            if legal and isinstance(self.chessboard[old_y][old_x], Pawn) and abs(old_y-new_y) == 2:
                flag_ep = True
                self.en_passant_x = old_x
                if white_turn and self.black_controlled[old_y+1][old_x]:
                    self.en_passant_y = old_y-1
                elif not white_turn and self.white_controlled[old_y-1][old_x]:
                    self.en_passant_y = old_y+1

        if not review_mode and legal:
            self.execute(old_x, old_y, new_x, new_y, white_turn)

            if self.en_passant:
                self.en_passant = False

            if flag_ep:
                self.en_passant = True

        return legal

    def execute(self, old_x, old_y, new_x, new_y, white_turn) -> None:
        if isinstance(self.chessboard[old_y][old_x], King):
            if new_x-old_x == 2:
                self.chessboard[old_y][new_x-1] = self.chessboard[old_y][new_x+1]
                self.chessboard[old_y][new_x+1] = None

            elif new_x-old_x == -2:
                self.chessboard[old_y][new_x+1] = self.chessboard[old_y][new_x-2]
                self.chessboard[old_y][new_x-2] = None

        if self.en_passant and isinstance(self.chessboard[old_y][old_x], Pawn)\
                and new_y == self.en_passant_y and new_x == self.en_passant_x:

            if white_turn:
                self.chessboard[new_y+1][new_x] = None
            else:
                self.chessboard[new_y-1][new_x] = None

        if self.promotion:
            if self.promote_to == "queen":
                self.chessboard[new_y][new_x] = Queen(white_turn)

            elif self.promote_to == "knight":
                self.chessboard[new_y][new_x] = Knight(white_turn)

            elif self.promote_to == "bishop":
                self.chessboard[new_y][new_x] = Bishop(white_turn)

            elif self.promote_to == "rook":
                self.chessboard[new_y][new_x] = Rook(white_turn)
        else:
            self.chessboard[old_y][old_x].has_moved = True
            self.chessboard[new_y][new_x] = self.chessboard[old_y][old_x]

        self.chessboard[old_y][old_x] = None
        self.update_controlled()

    def castle(self, old_x, old_y, new_x, new_y) -> bool:
        dx = new_x - old_x
        dy = new_y - old_y

        if dy:
            return False

        if dx > 0:
            rook_x = new_x + 1
            increment = 1
        else:
            rook_x = new_x - 2
            increment = -1

        if not self.chessboard[old_y][rook_x]:
            return False

        if self.jumps(old_x, old_y, rook_x, new_y):
            return False

        if self.chessboard[old_y][rook_x].has_moved or self.chessboard[old_y][old_x].has_moved:
            return False

        i = old_x
        while i != new_x + increment:
            if self.chessboard[old_y][old_x].is_white and self.black_controlled[old_y][i]:
                return False
            elif not self.chessboard[old_y][old_x].is_white and self.white_controlled[old_y][i]:
                return False
            i += increment
        return True

    def pin(self, old_x, old_y, new_x, new_y, white_turn, king_mode) -> bool:
        king_y = king_x = 0
        temp_chessboard = copy.deepcopy(self.chessboard)
        for i, j in itertools.product(range(8), range(8)):
            if self.chessboard[i][j] and isinstance(self.chessboard[i][j], King)\
                    and self.chessboard[i][j].is_white == white_turn:
                king_x = j
                king_y = i

        temp_chessboard[new_y][new_x] = temp_chessboard[old_y][old_x]
        temp_chessboard[old_y][old_x] = None

        temp_controlled = [[False for _ in range(8)] for _ in range(8)]
        for i, j in itertools.product(range(8), range(8)):
            if temp_chessboard[i][j] and temp_chessboard[i][j].is_white != white_turn:
                temp_controlled = temp_chessboard[i][j].controlled(temp_controlled, temp_chessboard, j, i)

        if king_mode:
            return temp_controlled[new_y][new_x]
        else:
            return temp_controlled[king_y][king_x]

    def jumps(self, old_x, old_y, new_x, new_y) -> bool:
        dx = abs(old_x-new_x)
        dy = abs(old_y-new_y)

        # check vertically
        if not dx:
            if new_y-old_y < 0:
                increment = -1
            else:
                increment = 1

            i = old_y + increment
            while i != new_y:
                if self.chessboard[i][new_x]:
                    return True
                i += increment

        # check horizontally
        elif not dy:
            if new_x-old_x < 0:
                increment = -1
            else:
                increment = 1

            i = old_x + increment
            while i != new_x:
                if self.chessboard[new_y][i]:
                    return True
                i += increment

        # check diagonally
        elif dx == dy:
            if new_x-old_x < 0:
                increment_x = -1
            else:
                increment_x = 1

            if new_y-old_y < 0:
                increment_y = -1
            else:
                increment_y = 1

            ix = old_x + increment_x
            iy = old_y + increment_y
            while ix != new_x and iy != new_y:
                if self.chessboard[iy][ix]:
                    return True
                ix += increment_x
                iy += increment_y

        return False

    def update_controlled(self) -> None:
        self.white_controlled = [[False for _ in range(8)] for _ in range(8)]
        self.black_controlled = [[False for _ in range(8)] for _ in range(8)]
        for i, j in itertools.product(range(8), range(8)):
            if self.chessboard[i][j] and self.chessboard[i][j].is_white:
                self.white_controlled = self.chessboard[i][j].controlled(self.white_controlled, self.chessboard, j, i)
            elif self.chessboard[i][j] and not self.chessboard[i][j].is_white:
                self.black_controlled = self.chessboard[i][j].controlled(self.black_controlled, self.chessboard, j, i)

    def can_promote(self, promote_to: str) -> bool:
        if promote_to is None:
            return False
        elif promote_to not in ("queen", "knight", "bishop", "rook"):
            return False
        else:
            self.promotion = True
            self.promote_to = promote_to
            return True

    def check(self, white_turn: bool) -> bool:
        king_y = king_x = 0
        for i, j in itertools.product(range(8), range(8)):
            if self.chessboard[i][j] and isinstance(self.chessboard[i][j], King)\
                    and self.chessboard[i][j].is_white == white_turn:
                king_x = j
                king_y = i

        if white_turn:
            return self.black_controlled[king_y][king_x]
        else:
            return self.white_controlled[king_y][king_x]

    def has_legal_move(self, white_turn: bool) -> bool:
        for i, j, k, l in itertools.product(range(8), range(8), range(8), range(8)):
            if self.gatekeeper(j, i, l, k, white_turn, True):
                return True
        return False

    def get_images(self) -> Tuple[str, str]:
        normal_board = 'temp/result-normal.png'
        flipped_board = 'temp/result-flipped.png'
        result_normal = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        result_flipped = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        result_normal.paste(self.board_normal_img, (0, 0))
        result_flipped.paste(self.board_flipped_img, (0, 0))

        for y, x in itertools.product(range(8), range(8)):
            if self.chessboard[y][x] is not None:
                piece_img = self.chessboard[y][x].img
                result_normal.paste(piece_img, (x * 64, y * 64), mask=piece_img)
                result_flipped.paste(piece_img, (448 - x * 64, 448 - y * 64), mask=piece_img)

        result_normal.save(normal_board)
        result_flipped.save(flipped_board)
        return normal_board, flipped_board
