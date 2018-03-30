from discord.ext import commands
import sys
import json
import asyncio
import traceback

try:
    with open('config.json', 'r') as file:
        config = json.loads(file.read())
        prefix = config['prefix']
        token = config['token']
except FileNotFoundError:
    print('config.json file not found! Exiting...')
    raise SystemExit

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
    print('__________________')


@bot.command(pass_context=True, hidden=True)
async def kill(ctx):
    bot_info = await bot.application_info()
    if ctx.message.author.id == bot_info.owner.id:
        print('Bot is being logged out.')
        print('__________________')
        await bot.say('Bye!')
        await bot.logout()
    else:
        await bot.say('Bye!')
        await asyncio.sleep(5)
        await bot.say('SIKE')


def main():
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            print(e)
            traceback.print_exc()
    bot.run(token)


if __name__ == '__main__':
    main()
