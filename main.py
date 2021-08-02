import discord
import epicgames
import asyncio
import datetime
import pytz
from discord.ext import tasks

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user: # If the message author is the bot, ignore the message.
        return

    if message.content == 'meow':
        await message.channel.send('meow')

    if message.content == 'meow free':
        await send_free_games(message.channel)


@tasks.loop(hours=24*7)
async def update_free_games():
    '''
    Sends a message to the update channel every time new games
    are available for free on Epic Games.
    '''

    channel = client.get_channel(871698820046655548)
    await channel.send('meow! new games available for free:')
    await send_free_games(channel)


@update_free_games.before_loop
async def before_update_free_games():
    '''
    Waits until the first Thursday at 6 PM to start the update
    free games loop.
    '''

    timezone = pytz.timezone('Asia/Jerusalem')

    for _ in range(60*60*24*7): # Loop the entire week until the first Thursday at 6 PM.
        d = datetime.datetime.now(timezone)  
        if d.hour == 18 and d.weekday() == epicgames.THURSDAY:
            return
        await asyncio.sleep(30) # Wait 30 seconds before looping again.


async def send_free_games(channel):
    '''
    Gets data of the games which are currently free and sends
    it to the specified channel.

    Parameters
    ----------
    channel : str
        The channel id to send the message to.
    '''

    games = epicgames.get_free_games()

    for game in games:
        await channel.send(embed=get_game_embed(game))

def get_game_embed(game):
    '''
    Returns a Discord embed for the given game object.

    Parameters
    ----------
    game : Game
        The game object to create an embed for.

    Returns
    -------
    discord.Embed
        Embed for the given game object.
    '''

    embed = discord.Embed()
    embed.title = game.get_name()
    embed.url = game.get_url()
    embed.set_image(url=game.get_image())

    return embed

# Get bot token from file and run the bot.
with open('token.txt', 'r') as token_file:
    token = token_file.read()

client.run(token)