from discord.ext import commands
from typing import Dict
import discord
import json
import math
import asyncio
import random


class Server:
    """Utility commmands for the server"""

    def __init__(self, bot):
        self.bot = bot
        self.challengers = {}  # type: Dict[str, Dict[str,str]]
        self.usernames = {}  # type: Dict[str, str]

        try:
            with open('ranks.json', 'r') as ranks_file:
                self.ranks = json.loads(ranks_file.read())
        except FileNotFoundError:
            self.ranks = {}  # type: Dict[str, Dict[str, float]]

    def update_ranks(self, server: str, stalemate: bool, winner: str, loser: str) -> None:
        sv_ranks = self.ranks[server]
        ows = sv_ranks[winner]
        ols = sv_ranks[loser]

        tr_winner = math.pow(10, sv_ranks[winner] / 400)
        tr_loser = math.pow(10, sv_ranks[loser] / 400)

        if not stalemate:
            sv_ranks[winner] = sv_ranks[winner] + 32 * (1 - tr_winner / (tr_winner + tr_loser))
            sv_ranks[loser] = sv_ranks[loser] - 32 * (tr_loser / (tr_winner + tr_loser))
        else:
            sv_ranks[winner] = sv_ranks[winner] + 32 * (0.5 - tr_winner / (tr_winner + tr_loser))
            sv_ranks[loser] = sv_ranks[loser] + 32 * (0.5 - tr_loser / (tr_winner + tr_loser))

        print(f'{self.usernames[winner]} score change: {ows} -> {sv_ranks[winner]}')
        print(f'{self.usernames[loser]} score change: {ols} -> {sv_ranks[loser]}')
        print('__________________')

        with open('ranks.json', 'w') as file:
            json.dump(self.ranks, file)
            print('Ranks saved to \'ranks.json\'!')
            print('__________________')

    def save_ranks(self) -> None:
        with open('ranks.json', 'w') as file:
            json.dump(self.ranks, file)

    async def timeout(self, challengers: Dict[str, str], clr: str, cld: str) -> None:
        challengers[clr] = cld
        await asyncio.sleep(60)
        if clr in challengers and challengers[clr] == cld:
            challengers.pop(clr)
            await self.bot.say(f'Challenge by <@{clr}> timed out!')

    @commands.command(pass_context=True, description='Request an user to play a game, must mention the user.')
    async def challenge(self, ctx, user: discord.Member=None):
        """Challenge an user."""
        if user is None:
            await self.bot.say('You have to specify who you\'re fighting!')
            await self.bot.say(f'(ex: `{self.bot.command_prefix}challenge @{ctx.message.author}`)')
        else:
            author_id = ctx.message.author.id
            sv_id = ctx.message.server.id

            if sv_id not in self.challengers:
                self.challengers[sv_id] = {}

            sv_challengers = self.challengers[sv_id]
            if author_id in sv_challengers and sv_challengers[author_id] == user.id:
                await self.bot.say('You\'re already challenging this user!')
            elif author_id == user.id:
                await self.bot.say('You can\'t challenge yourself!')
            elif user.id == self.bot.user.id:
                await self.bot.say('I don\'t know how to play chess (yet)!')
            else:
                await self.bot.say(f'Challenging {user.name}! Say `{self.bot.command_prefix}accept` to accept.')
                await self.timeout(sv_challengers, author_id, user.id)

    @commands.command(pass_context=True, description='Accept all game requests you chould have.')
    async def accept(self, ctx):
        """Accept challenges."""
        user_id = ctx.message.author.id
        sv_id = ctx.message.server.id

        if sv_id not in self.challengers:
            self.challengers[sv_id] = {}

        sv_challengers = self.challengers[sv_id]
        if user_id not in sv_challengers.values():
            await self.bot.say('You don\'t have any requests!')
        else:
            for clr, cld in sv_challengers.copy().items():
                if user_id == cld:
                    # start game
                    if clr not in self.usernames:
                        self.usernames[clr] = await self.bot.get_user_info(clr)
                    if cld not in self.usernames:
                        self.usernames[cld] = ctx.message.author

                    players = [clr, cld]
                    random.shuffle(players)
                    white, black = players

                    game_cog = self.bot.cogs['Game']
                    game_cog.new_game(white, black, sv_id)
                    sv_challengers.pop(clr)
                    await self.bot.say(f'New match started: id `{game_cog.last_game_id}`, '
                                       f'<@{white}> (white) vs <@{black}> (black). '
                                       f'Say `{self.bot.command_prefix}help move` to learn how to move!')
                    board_normal, _ = game_cog.games[game_cog.last_game_id].img_path()
                    await self.bot.upload(board_normal)

    @commands.command(pass_context=True, description='Shows you all the games you\'re part of.')
    async def remember(self, ctx):
        """Show all your games."""
        user_id = ctx.message.author.id
        msg = '```Your games:\n'
        game_cog = self.bot.cogs['Game']

        for gid, game in game_cog.games.items():
            if user_id in (game.white, game.black):
                msg += f'id {game.game_id}: {game.white_name}(w) vs {game.black_name}(b)\n'
        msg += '```'
        await self.bot.say(msg)

    @commands.command(pass_context=True, description='Shows the ranks in your server. Play a match to get a rank!')
    async def rankings(self, ctx):
        """Show rankings."""
        sv_id = ctx.message.server.id

        if sv_id not in self.ranks:
            self.ranks[sv_id] = {}

        sv_ranks = self.ranks[sv_id]
        for user_id in sv_ranks:
            if user_id not in self.usernames:
                self.usernames[user_id] = str(await self.bot.get_user_info(user_id))

        rank = 1
        msg = '```Server rankings:\n'
        for user_id in sorted(sv_ranks, key=sv_ranks.get, reverse=True):
            msg += f'#{rank} {self.usernames[user_id]} {sv_ranks[user_id]}\n'
            rank += 1
        msg += '```'
        await self.bot.say(msg)


def setup(bot):
    bot.add_cog(Server(bot))
