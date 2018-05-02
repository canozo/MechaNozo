from discord.ext import commands
import basc_py4chan as py4chan
import discord
import random
import math


class Misc:
    """Misc commands."""
    def __init__(self, bot):
        self.bot = bot
        self.help_dict = {}

    @commands.command(name='help')
    async def _help(self, ctx, command: str = None):
        """Show all of the available commands and how to use specific commands."""
        embed = discord.Embed(title=f'{self.bot.user.name} help', type='rich', colour=discord.Colour.magenta())
        if command is None:
            embed.description = f'List of available commands, type ' \
                                f'`{self.bot.command_prefix}help command` to get more info!'
            for cog, cmd_dict in self.help_dict.items():
                value = ''
                for cmd in cmd_dict:
                    value += f'`{cmd}` '
                embed.add_field(name=f'{cog} commands', value=value, inline=False)

        else:
            found = False
            help_msg = None
            usage = []
            for _, cmd_dict in self.help_dict.items():
                if command in cmd_dict:
                    found = True
                    help_msg, params = cmd_dict[command]
                    usage.append(f'{self.bot.command_prefix}{command}')

                    for var, param in params.items():
                        if var not in ('self', 'ctx'):
                            usage.append(var)
                            embed.add_field(name=f'Parameter: {var}', value=f'`{param}`', inline=False)

            if found:
                embed.title = f'Command: {command}'
                embed.description = f'{help_msg}'
                embed.add_field(name='Usage', value='`' + ' '.join(usage) + '`', inline=False)
            else:
                embed.description = f'There is no help for command `{command}`! Maybe it doesn\'t exist?'
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def kill(self, ctx):
        if await ctx.bot.is_owner(ctx.author):
            print('Bot is being logged out.')
            print('__________________')
            message = await ctx.send('*commits sudoku*')
            await message.add_reaction('\U0001f1eb')
            await self.bot.change_presence(status=discord.Status.offline)
            await self.bot.logout()

    @commands.command()
    async def roll(self, ctx):
        """Get a number from 1 to 100."""
        num = math.ceil((1 - math.pow(random.random(), 0.26)) * 100)
        await ctx.send(f'{ctx.author.name} rolled `{num}`!')

    @commands.command(name='4chan')
    async def fourchan(self, ctx, letter: str='jp'):
        """Get a random image from a board on 4chan (defaults to `/jp/`)."""
        board = py4chan.Board(letter)
        try:
            sfw = board.is_worksafe
        except KeyError:
            await ctx.send(f'Board `/{letter}/` doesn\'t exist!')
        else:
            if not sfw and not ctx.channel.is_nsfw():
                await ctx.send(f'Board `/{letter}/` is nsfw and this channel is sfw!')
            else:
                thread_id = random.choice(board.get_all_thread_ids())
                thread = board.get_thread(thread_id)
                file_url = random.choice(list(thread.files()))
                await ctx.send(file_url)


def setup(bot):
    bot.remove_command('help')
    bot.add_cog(Misc(bot))

    help_dict = bot.cogs['Misc'].help_dict
    for cmd, obj in bot.all_commands.items():
        if not obj.hidden:
            category = obj.module.split('.')[1].title()
            if category not in help_dict:
                help_dict[category] = {}
            cmd_dict = help_dict[category]
            cmd_dict[cmd] = (obj.help, obj.params)
