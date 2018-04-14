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

extensions = [
    'cogs.game',
    'cogs.misc'
]

bot_description = 'Simple bot mostly used for playing chess matches on discord.'
bot = commands.Bot(command_prefix=prefix, description=bot_description)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('?help'))
    print(f'{bot.user.name} ({bot.user.id}) is up and running!')
    print('__________________')


@bot.event
async def on_command_error(ctx, exception):
    ignore = (commands.CommandNotFound, commands.BadArgument, commands.UserInputError, commands.MissingRequiredArgument)
    if isinstance(exception, ignore):
        return

    print(f'Exception in command {ctx.command}', file=sys.stderr)
    traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)
    print('__________________', file=sys.stderr)


def main():
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as exc:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            print(exc)
            traceback.print_exc()

    bot.usernames = {}
    bot.run(token)


if __name__ == '__main__':
    main()
