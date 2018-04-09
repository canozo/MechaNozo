from typing import Tuple
import board


class Chess:
    def __init__(self, white: int, black: int, game_id: int, guild_id: int):
        self.white = white
        self.black = black
        self.game_id = game_id
        self.guild_id = guild_id
        self.board = board.Board()
        self.white_turn = True
        self.gameover = False
        self.old_x = 0
        self.old_y = 0
        self.new_x = 0
        self.new_y = 0

    def img_path(self) -> Tuple[str, str]:
        return self.board.get_images()

    def move(self, player_id: int, mv_from: str, mv_into: str, promote_to: str=None) -> int:
        if (self.white_turn and player_id != self.white) or (not self.white_turn and player_id != self.black):
            # not the players turn
            return 1

        elif len(mv_from) != 2 or len(mv_into) != 2 or mv_from[0] not in 'abcdefgh' or mv_from[1] not in '12345678'\
                or mv_into[0] not in 'abcdefgh' or mv_into[1] not in '12345678':
            # wrote the move incorrectly
            return 2

        else:
            self.old_x = 'abcdefgh'.find(mv_from[0])
            self.old_y = '87654321'.find(mv_from[1])
            self.new_x = 'abcdefgh'.find(mv_into[0])
            self.new_y = '87654321'.find(mv_into[1])

            if not self.board.gatekeeper(
                    self.old_x, self.old_y, self.new_x, self.new_y, self.white_turn, False, promote_to):
                # illegal move
                return 3

            else:
                # move executed
                self.white_turn = not self.white_turn

                # checkmate happened
                if self.board.check(self.white_turn) and not self.board.has_legal_move(self.white_turn):
                    self.gameover = True

                # stalemate happened
                elif not self.board.has_legal_move(self.white_turn):
                    self.gameover = True
                return 0

    def status(self) -> Tuple[bool, bool]:
        # returns the current status of the game (is game over, is stalemate)
        return self.gameover, self.gameover and not self.board.check(self.white_turn)

    def surrender(self, player_id: int) -> int:
        winner = None

        if player_id == self.white:
            self.gameover = True
            winner = self.black

        elif player_id == self.black:
            self.gameover = True
            winner = self.white

        return winner
