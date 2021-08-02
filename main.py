from asyncio.tasks import wait
import discord
import epicgames
import asyncio
import datetime
import pytz
from discord.ext import tasks

COMMANDS = {
    'meow': 'replies with "meow".',
    'free': 'sends the games which are currently free on epic games.',
    'commands': "sends a list of the bot's commands.",
    'help <command>': 'sends the description of the requested command.',
    'update': 'sends a list of the commands added in the last update, and the commands to be added in the upcoming update.'
}

UPDATE = {
    'last': {

    },
    'upcoming': {

    }
}

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    update_free_games.start()
    remind_free_games.start()

@client.event
async def on_message(message):
    if message.author == client.user: # If the message author is the bot, ignore the message.
        return

    if message.content == 'meow':
        await message.channel.send('meow')

    elif message.content == 'meow commands':
        await message.channel.send(embed=get_commands())

    elif message.content.startswith('meow help'):
        await message.channel.send(embed=get_help(message.content.split()[-1]))

    elif message.content == 'meow free':
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

    await wait_until_time(epicgames.THURSDAY)


@tasks.loop(hours=24*7)
async def remind_free_games():
    '''
    Sends a reminder to the update channel 24 hours before new games
    are available for free on Epic Games.
    '''

    channel = client.get_channel(871698820046655548)
    await channel.send("meow! don't forget to get this week's free games:")
    await send_free_games(channel)


@remind_free_games.before_loop
async def before_remind_free_games():
    '''
    Waits until the first Wednesday at 6 PM to start the remind
    free games loop.
    '''

    await wait_until_time(epicgames.WEDNESDAY)


async def wait_until_time(weekday):
    '''
    Waits until the given weekday at 6 PM and returns.
    '''

    timezone = pytz.timezone('Asia/Jerusalem')

    for _ in range(60*60*24*7): # Loop the entire week until the given weekday at 6 PM.
        d = datetime.datetime.now(timezone)  
        if d.hour == 18 and d.weekday() == weekday:
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


def get_commands():
    '''
    Returns a Discord embed containing the bot's command list.

    Returns
    -------
    discord.Embed
        Embed containing the bot's command list.
    '''    
    
    commands_str = ''

    for name, description in COMMANDS.items():
        commands_str += '`meow {}` - {}\n\n'.format(name, description)

    embed = discord.Embed()
    embed.title = 'meow commands ♡'
    embed.set_thumbnail(url='https://media2.giphy.com/media/6bXd6ZTYpZWrC/source.gif')
    embed.description = '`'+ commands_str[6:] # Remove first meow.
    embed.color = discord.Color.from_rgb(255, 232, 239)

    return embed


def get_help(command_name):
    '''
    Returns a Discord embed containing the requested command's description.
    If the command doesn't exist, returns an error message.

    Returns
    -------
    discord.Embed
        Embed containing the requested command's description or an error message.
    '''

    command_name = command_name.lower()
    embed = discord.Embed()
    embed.set_thumbnail(url='https://66.media.tumblr.com/tumblr_maorfzn99Q1rfjowdo1_500.gif')
    embed.color = discord.Color.from_rgb(255, 232, 239)

    if command_name in COMMANDS.keys(): 
        embed.title = 'meow ' + command_name
        embed.description = COMMANDS[command_name]
    
    elif command_name == 'help':
        embed.description = 'please enter a command name in the following format: `meow help <command>` to get information on the requested command.'
    
    else:
        embed.description = "the command `{}` doesn't exist. for command suggestions message <@!536826296009883649>.".format(command_name)
    
    return embed


# Get bot token from file and run the bot.
with open('token.txt', 'r') as token_file:
    token = token_file.read()

client.run(token)