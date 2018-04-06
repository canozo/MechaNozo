from discord.ext import commands
import sys
import json
import asyncio
import traceback

try:
    with open('config.json', 'r') as file:
        config = json.loads(file.read())
        prefix: str = config['prefix']
        print_traceback: bool = config['print traceback']
        token: str = config['token']

except FileNotFoundError:
    print('config.json file not found! Exiting...')
    sys.exit()

except KeyError:
    print('config.json file missing a key! Exiting...')
    sys.exit()

extensions = [
    'cogs.game',
    'cogs.server'
]

bot_description = '''chess-tan!
Simple chess bot for playing chess matches on discord, making using of discord.py.'''
bot = commands.Bot(command_prefix=prefix, description=bot_description)


@bot.event
async def on_ready():
    print(f'{bot.user.name} ({bot.user.id}) is up and running!')
    if print_traceback:
        print('print_traceback is enabled!')
    else:
        print('print_traceback is disabled! Change your config.json file to enable it.')
    print('__________________')


@bot.event
async def on_command_error(exception, context):
    if hasattr(context.command, 'on_error'):
        return

    print(f'Ignoring exception in command {context.command}', file=sys.stderr)
    if print_traceback:
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)
    print('__________________', file=sys.stderr)


@bot.command(pass_context=True, hidden=True)
async def kill(ctx):
    await bot.say('Bye!')
    bot_info = await bot.application_info()
    if ctx.message.author.id == bot_info.owner.id:
        print('Bot is being logged out.')
        print('__________________')
        await bot.logout()
    else:
        await asyncio.sleep(5)
        await bot.say('SIKE')


def main():
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as exc:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            print(exc)
            traceback.print_exc()
    bot.run(token)


if __name__ == '__main__':
    main()
