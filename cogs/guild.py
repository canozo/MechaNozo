from discord.ext import commands
from typing import Dict
import discord
import json
import math
import asyncio
import random


class Guild:
    """Utility commmands for the guild"""

    def __init__(self, bot):
        self.bot = bot
        self.ranks = {}  # type: Dict[int, Dict[int, float]]
        self.requests = {}  # type: Dict[int, Dict[int, int]]
        self.usernames = {}  # type: Dict[int, str]

        try:
            with open('ranks.json', 'r') as ranks_file:
                raw_dict = json.loads(ranks_file.read())
                self.ranks = {int(g): {int(i): e for i, e in raw_dict[g].items()} for g, r in raw_dict.items()}

        except FileNotFoundError:
            pass

    def update_ranks(self, guild_id: int, stalemate: bool, winner: int, loser: int) -> None:
        guild_ranks = self.ranks[guild_id]
        ows = guild_ranks[winner]
        ols = guild_ranks[loser]

        tr_winner = math.pow(10, guild_ranks[winner] / 400)
        tr_loser = math.pow(10, guild_ranks[loser] / 400)

        if not stalemate:
            guild_ranks[winner] = guild_ranks[winner] + 32 * (1 - tr_winner / (tr_winner + tr_loser))
            guild_ranks[loser] = guild_ranks[loser] - 32 * (tr_loser / (tr_winner + tr_loser))
        else:
            guild_ranks[winner] = guild_ranks[winner] + 32 * (0.5 - tr_winner / (tr_winner + tr_loser))
            guild_ranks[loser] = guild_ranks[loser] + 32 * (0.5 - tr_loser / (tr_winner + tr_loser))

        print(f'{self.usernames[winner]} score change: {ows} -> {guild_ranks[winner]}')
        print(f'{self.usernames[loser]} score change: {ols} -> {guild_ranks[loser]}')
        print('__________________')

        with open('ranks.json', 'w') as file:
            json.dump(self.ranks, file)
            print('Ranks saved to \'ranks.json\'!')
            print('__________________')

    @staticmethod
    async def timeout(ctx, guild_reqs: Dict[int, int], clr: int, cld: int) -> None:
        guild_reqs[clr] = cld
        await asyncio.sleep(60)

        if clr in guild_reqs and guild_reqs[clr] == cld:
            guild_reqs.pop(clr)
            await ctx.send(f'Challenge by <@{clr}> timed out!')

    @commands.command(description='Request an user to play a game, must mention the user.')
    async def challenge(self, ctx, user: discord.Member=None):
        """Challenge an user."""
        if user is None:
            await ctx.send('You have to specify who you\'re challenging! '
                           f'(ex: `{self.bot.command_prefix}challenge @{ctx.author}`)')
        else:
            author_id = ctx.author.id
            guild_id = ctx.guild.id

            if guild_id not in self.requests:
                self.requests[guild_id] = {}

            guild_reqs = self.requests[guild_id]

            if author_id in guild_reqs and guild_reqs[author_id] == user.id:
                await ctx.send('You\'re already challenging this user!')

            elif author_id == user.id:
                await ctx.send('You can\'t challenge yourself!')

            elif user.id == self.bot.user.id:
                await ctx.send('I don\'t know how to play chess (yet)!')

            else:
                await ctx.send(f'Challenging {user.name}! Say `{self.bot.command_prefix}accept` to accept.')
                await self.timeout(ctx, guild_reqs, author_id, user.id)

    @commands.command(description='Accept all game requests you chould have.')
    async def accept(self, ctx):
        """Accept challenges."""
        user_id = ctx.author.id
        guild_id = ctx.guild.id

        if guild_id not in self.requests:
            self.requests[guild_id] = {}

        guild_reqs = self.requests[guild_id]

        if user_id not in guild_reqs.values():
            await ctx.send('You don\'t have any requests!')
        else:
            for clr, cld in guild_reqs.copy().items():
                if user_id == cld:
                    # start game
                    if clr not in self.usernames:
                        self.usernames[clr] = await self.bot.get_user_info(clr)
                    if cld not in self.usernames:
                        self.usernames[cld] = ctx.author

                    players = [clr, cld]
                    random.shuffle(players)
                    white, black = players

                    game_cog = self.bot.cogs['Game']
                    game_cog.new_game(white, black, guild_id)
                    guild_reqs.pop(clr)

                    msg = f'New match started: id `{game_cog.last_game_id}`, '\
                          f'<@{white}> (white) vs <@{black}> (black). '\
                          f'Say `{self.bot.command_prefix}help move` to learn how to move!'

                    board_normal, _ = game_cog.games[game_cog.last_game_id].img_path()
                    await ctx.send(msg, file=discord.File(board_normal, 'board.png'))

    @commands.command(description='Shows you all the games you\'re part of.')
    async def remember(self, ctx):
        """Show all your games."""
        user_id = ctx.author.id
        game_cog = self.bot.cogs['Game']
        msg = '```Your games:\n'

        for _, game in game_cog.games.items():
            if user_id in (game.white, game.black):
                msg += f'id {game.game_id}: {self.usernames[game.white]}(w) vs {self.usernames[game.black]}(b)\n'

        msg += '```'
        await ctx.send(msg)

    @commands.command(description='Shows the ranks in your guild. Play a match to get a rank!')
    async def rankings(self, ctx):
        """Show rankings."""
        guild_id = ctx.guild.id

        if guild_id not in self.ranks:
            self.ranks[guild_id] = {}

        guild_ranks = self.ranks[guild_id]

        for user_id in guild_ranks:
            if user_id not in self.usernames:
                self.usernames[user_id] = await self.bot.get_user_info(user_id)

        rank = 1
        msg = '```Guild rankings:\n'

        for user_id in sorted(guild_ranks, key=guild_ranks.get, reverse=True):
            msg += f'#{rank} {self.usernames[user_id]} {guild_ranks[user_id]}\n'
            rank += 1

        msg += '```'
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(Guild(bot))
