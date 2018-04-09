from discord.ext import commands
import sys
import json
import discord
import traceback

try:
    with open('config.json', 'r') as file:
        config = json.loads(file.read())
        prefix: str = config['prefix']
        token: str = config['token']

except FileNotFoundError:
    print('config.json file not found! Exiting...')
    sys.exit()

except KeyError:
    print('config.json missing a key! Exiting...')
    sys.exit()

help_dict = {}
extensions = [
    'cogs.game',
    'cogs.guild'
]

bot_description = '''smug-bot!
Simple bot for playing chess matches on discord.'''
bot = commands.Bot(command_prefix=prefix, description=bot_description)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('?help'))
    print(f'{bot.user.name} ({bot.user.id}) is up and running!')
    print('__________________')


@commands.command(name='help', hidden=True)
async def _help(ctx, command: str=None):
    embed = discord.Embed(title='smug-bot help', type='rich', colour=discord.Colour.magenta())
    if command is None:
        embed.description = f'List of available commands, type `{prefix}help command` to get more info!'
        for cog, cmd_dict in help_dict.items():
            value = ''
            for cmd in cmd_dict:
                value += f'`{cmd}` '
            embed.add_field(name=cog, value=value, inline=False)

    elif command != 'help':
        found = False
        help_msg = None
        usage = []
        for _, cmd_dict in help_dict.items():
            if command in cmd_dict:
                found = True
                help_msg, params = cmd_dict[command]
                usage.append(f'{prefix}{command}')

                for var, param in params.items():
                    if var not in ('self', 'ctx'):
                        usage.append(var)
                        embed.add_field(name=f'Parameter {var}', value=f'`{param}`', inline=False)

        if found:
            embed.title = command
            embed.description = f'{help_msg}'
            embed.add_field(name='Usage', value='`'+' '.join(usage)+'`', inline=False)
        else:
            embed.description = 'This command doesn\'t exist!!'
    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, exception):
    ignore = (commands.CommandNotFound, commands.BadArgument, commands.UserInputError, commands.MissingRequiredArgument)
    if isinstance(exception, ignore):
        return

    print(f'Exception in command {ctx.command}', file=sys.stderr)
    traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)
    print('__________________', file=sys.stderr)


@bot.command(hidden=True)
async def kill(ctx):
    if await ctx.bot.is_owner(ctx.author):
        print('Bot is being logged out.')
        print('__________________')
        await ctx.send('Bye!')
        await bot.change_presence(status=discord.Status.offline)
        await bot.logout()


def main():
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as exc:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            print(exc)
            traceback.print_exc()

    bot.remove_command('help')
    bot.add_command(_help)

    for cmd, obj in bot.all_commands.items():
        if not obj.hidden:
            category = obj.module.split('.')[1].title()
            if category not in help_dict:
                help_dict[category] = {}
            cmd_dict = help_dict[category]
            cmd_dict[cmd] = (obj.help, obj.params)

    bot.run(token)


if __name__ == '__main__':
    main()
