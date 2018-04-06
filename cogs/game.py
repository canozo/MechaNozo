from discord.ext import commands
from typing import Dict
import chess


class Game:
    """Commands for specific chess games."""

    def __init__(self, bot):
        self.bot = bot
        self.games = {}  # type: Dict[int, chess.Match]
        self.last_game_id = 0

    async def verify_game(self, game_id: int, user_id: str, server_id: str) -> bool:
        if game_id not in self.games:
            await self.bot.say(f'No games with id {game_id} found. '
                               f'Say `{self.bot.command_prefix}remember` to see your games!')
            return False
        elif self.games[game_id].sv_id != server_id:
            await self.bot.say('This game does not correspond to this server. '
                               'Please go back to the server where this game started!')
            return False
        elif user_id not in (self.games[game_id].white, self.games[game_id].black):
            await self.bot.say('You don\'t belong to that game. '
                               f'Say `{self.bot.command_prefix}remember` to see your games!')
            return False
        else:
            return True

    def new_game(self, white: str, black: str, sv_id: str) -> None:
        self.last_game_id += 1

        ranks = self.bot.cogs['Server'].ranks
        usernames = self.bot.cogs['Server'].usernames

        if sv_id not in ranks:
            ranks[sv_id] = {}

        sv_ranks = ranks[sv_id]
        if white not in sv_ranks:
            sv_ranks[white] = 1000.0
        if black not in sv_ranks:
            sv_ranks[black] = 1000.0

        self.games[self.last_game_id] = chess.Match(white, black, self.last_game_id, sv_id)
        print(f'New match starting on server {sv_id}:')
        print(f'id {self.last_game_id}, {usernames[white]}(id {white})(white) vs {usernames[black]}(id {black})(black)')
        print('__________________')

    @commands.command(pass_context=True, description='Show the chessboard flipped to your side.')
    async def board(self, ctx, game_id: int):
        """Show the board."""
        user_id = ctx.message.author.id
        sv_id = ctx.message.server.id

        if await self.verify_game(game_id, user_id, sv_id):
            match = self.games[game_id]
            board_normal, board_flipped = match.img_path()
            if user_id == match.white:
                await self.bot.upload(board_normal)
            else:
                await self.bot.upload(board_flipped)

    @commands.command(pass_context=True, description='Forfeit an ongoing game you\'re part of.')
    async def surrender(self, ctx, game_id: int):
        """Forfeit."""
        user_id = ctx.message.author.id
        sv_id = ctx.message.server.id

        if await self.verify_game(game_id, user_id, sv_id):
            gameover, winner = self.games[game_id].surrender(user_id)
            await self.bot.say(f'<@{user_id}> surrenders, <@{winner}> wins!')
            server_cog = self.bot.cogs['Server']
            server_cog.update_ranks(sv_id, False, winner, user_id)
            self.games.pop(game_id)

    @commands.command(pass_context=True, description='Execute a move, moves are formatted like such: d2 d4, b8 c6, etc')
    async def move(self, ctx, game_id: int, fr: str, to: str, promotion: str=None):
        """Make a move."""
        user_id = ctx.message.author.id
        sv_id = ctx.message.server.id

        if await self.verify_game(game_id, user_id, sv_id):
            match = self.games[game_id]
            error = match.move(user_id, fr, to, promotion)

            if not error:
                board_normal, board_flipped = match.img_path()
                if match.white_turn:
                    await self.bot.upload(board_normal)
                else:
                    await self.bot.upload(board_flipped)

                gameover, stalemate = match.status()
                if user_id == match.white:
                    player_two = match.black
                else:
                    player_two = match.white

                if stalemate:
                    await self.bot.say(f'<@{player_two}> and <@{user_id}> tied!')
                    server_cog = self.bot.cogs['Server']
                    server_cog.update_ranks(sv_id, stalemate, user_id, player_two)
                    self.games.pop(game_id)
                elif gameover:
                    await self.bot.say(f'<@{player_two}> got checkmated, <@{user_id}> wins!')
                    server_cog = self.bot.cogs['Server']
                    server_cog.update_ranks(sv_id, stalemate, user_id, player_two)
                    self.games.pop(game_id)
                elif match.white_turn:
                    await self.bot.say('Move executed! White turn.')
                else:
                    await self.bot.say('Move executed! Black turn.')

            elif error == 1:
                # not the players turn
                await self.bot.say('It\'s not your turn yet!')
            elif error == 2:
                # wrote move incorrectly
                await self.bot.say(f'`{fr} {to}` is not a valid move. '
                                   'Moves are formatted like such: d2 d4, b8 c6, etc.')
            elif error == 3:
                # made an illegal move
                await self.bot.say(f'`{fr} {to}` is an illegal move!')


def setup(bot):
    bot.add_cog(Game(bot))
