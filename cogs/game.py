from discord.ext import commands
from chess import Chess
from typing import Dict
import discord


class Game:
    """Commands for specific chess games."""

    def __init__(self, bot):
        self.bot = bot
        self.games = {}  # type: Dict[int, Chess]
        self.last_game_id = 0

    async def verify_game(self, ctx, game_id: int, user_id: int, guild_id: int) -> bool:
        if game_id not in self.games:
            await ctx.send(f'No games with id {game_id} found. '
                           f'Say `{self.bot.command_prefix}remember` to see your games!')
            return False

        elif self.games[game_id].guild_id != guild_id:
            await ctx.send('This game does not correspond to this guild. '
                           'Please go back to the guild where this game started!')
            return False

        elif user_id not in (self.games[game_id].white, self.games[game_id].black):
            await ctx.send('You don\'t belong to that game. '
                           f'Say `{self.bot.command_prefix}remember` to see your games!')
            return False

        else:
            return True

    def new_game(self, white: int, black: int, guild_id: int) -> None:
        self.last_game_id += 1
        ranks = self.bot.cogs['Guild'].ranks
        usernames = self.bot.cogs['Guild'].usernames

        if guild_id not in ranks:
            ranks[guild_id] = {}

        guild_ranks = ranks[guild_id]

        if white not in guild_ranks:
            guild_ranks[white] = 1000.0
        if black not in guild_ranks:
            guild_ranks[black] = 1000.0

        self.games[self.last_game_id] = Chess(white, black, self.last_game_id, guild_id)
        print(f'New match starting on guild {guild_id}:')
        print(f'id {self.last_game_id}, {usernames[white]}(id {white})(white) vs {usernames[black]}(id {black})(black)')
        print('__________________')

    @commands.command(description='Show the chessboard flipped to your side.')
    async def board(self, ctx, game_id: int):
        """Show the board."""
        user_id = ctx.author.id
        guild_id = ctx.guild.id

        if await self.verify_game(ctx, game_id, user_id, guild_id):
            match = self.games[game_id]
            board_normal, board_flipped = match.img_path()

            if match.white_turn:
                msg = 'White turn:'
            else:
                msg = 'Black turn:'

            if user_id == match.white:
                await ctx.send(msg, file=discord.File(board_normal, 'board.png'))
            else:
                await ctx.send(msg, file=discord.File(board_flipped, 'board.png'))

    @commands.command(description='Forfeit an ongoing game you\'re part of.')
    async def surrender(self, ctx, game_id: int):
        """Forfeit."""
        user_id = ctx.author.id
        guild_id = ctx.guild.id

        if await self.verify_game(ctx, game_id, user_id, guild_id):
            winner = self.games[game_id].surrender(user_id)
            await ctx.send(f'<@{user_id}> surrenders, <@{winner}> wins!')

            guild_cog = self.bot.cogs['Guild']
            guild_cog.update_ranks(guild_id, False, winner, user_id)
            self.games.pop(game_id)

    @commands.command(description='Execute a move, moves are formatted like such: d2 d4, b8 c6, etc')
    async def move(self, ctx, game_id: int, fr: str, to: str, promotion: str=None):
        """Make a move."""
        user_id = ctx.author.id
        guild_id = ctx.guild.id

        if await self.verify_game(ctx, game_id, user_id, guild_id):
            match = self.games[game_id]
            error = match.move(user_id, fr, to, promotion)

            if not error:
                board_normal, board_flipped = match.img_path()
                gameover, stalemate = match.status()

                if user_id == match.white:
                    player_two = match.black
                else:
                    player_two = match.white

                if stalemate:
                    msg = f'<@{player_two}> and <@{user_id}> tied!'
                    guild_cog = self.bot.cogs['Guild']
                    guild_cog.update_ranks(guild_id, stalemate, user_id, player_two)
                    self.games.pop(game_id)

                elif gameover:
                    msg = f'<@{player_two}> got checkmated, <@{user_id}> wins!'
                    guild_cog = self.bot.cogs['Guild']
                    guild_cog.update_ranks(guild_id, stalemate, user_id, player_two)
                    self.games.pop(game_id)

                elif match.white_turn:
                    msg = 'Move executed! White turn:'
                else:
                    msg = 'Move executed! Black turn:'

                if match.white_turn:
                    await ctx.send(msg, file=discord.File(board_normal, 'board.png'))
                else:
                    await ctx.send(msg, file=discord.File(board_flipped, 'board.png'))

            elif error == 1:
                # not the players turn
                await ctx.send('It\'s not your turn yet!')

            elif error == 2:
                # wrote move incorrectly
                await ctx.send(f'`{fr} {to}` is not a valid move. '
                               'Moves are formatted like such: `d2 d4`, `b8 c6`, `a1 h8` etc.')

            elif error == 3:
                # made an illegal move
                await ctx.send(f'`{fr} {to}` is an illegal move!')


def setup(bot):
    bot.add_cog(Game(bot))
