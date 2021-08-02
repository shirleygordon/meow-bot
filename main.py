from asyncio.tasks import wait
import discord
from discord.embeds import Embed
import epicgames
import asyncio
import datetime
import pytz
from discord.ext import tasks

class MeowCommand:
    def __init__(self, name, description, function=None):
        self._name = name
        self._description = description
        self._function = function

    def get_name(self):
        return self._name

    def get_description(self):
        return self._description

    def get_function(self):
        return self._function
        

UPDATE = {
    'last': ['commands', 'help', 'update', 'set-update-channel'],
    'upcoming': {
        'rating <game-name>': 'sends the average rating of the requested game, based on information from different websites.',
        'sale': 'sends a list of games which are currently on sale on different websites, like epic games, steam, origin, etc.',
        'sale <website>': 'sends a list of games which are currently on sale on the requested website.',
        'notify-sale <game-name>': 'sends a message when the requested game is on sale. also sends a private message to the user who ran the command.',
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

    elif message.content.startswith('meow '):
        command = message.content[5:]
        
        for meow_command in COMMANDS:
            if meow_command.get_name().split()[0] == command.lower().split()[0]:
                await meow_command.get_function()(message)
                break


async def send_commands(message):
    '''
    Sends a message containing the bot's command list.

    Parameters
    ----------
    message - discord.Message
        Message containing the command.
    '''    
    
    commands_str = ''

    for command in COMMANDS:
        commands_str += '`meow {}` - {}\n\n'.format(command.get_name(), command.get_description())

    embed = discord.Embed()
    embed.title = 'meow commands ♡'
    embed.set_thumbnail(url='https://media2.giphy.com/media/6bXd6ZTYpZWrC/source.gif')
    embed.description = '`'+ commands_str[6:] # Remove first meow.
    embed.color = discord.Color.from_rgb(255, 232, 239)

    await message.channel.send(embed=embed)


async def send_help(message):
    '''
    Sends a message containing the requested command's description.
    If the command doesn't exist, sends an error message.

    Parameters
    ----------
    message - discord.Message
        Message containing the command.
    '''

    found = False
    command_name = message.content.split()[-1].lower()
    embed = discord.Embed()
    embed.set_thumbnail(url='https://66.media.tumblr.com/tumblr_maorfzn99Q1rfjowdo1_500.gif')
    embed.color = discord.Color.from_rgb(255, 232, 239)

    for command in COMMANDS:
        if command.get_name().split()[0] == command_name:
            embed.title = 'meow ' + command.get_name()
            embed.description = command.get_description()
            found = True
            break
    
    if not found:
        embed.description = "the command `{}` doesn't exist. for command suggestions message <@!536826296009883649>.".format(command_name)
    
    await message.channel.send(embed=embed)


async def send_update(message):
    '''
    Sends a message containing a list of the commands added in the last update,
    and the commands to be added in the upcoming update.

    Parameters
    ----------
    message - discord.Message
        Message containing the command.
    '''
    
    embed = discord.Embed()
    embed.set_thumbnail(url='')
    embed.color = discord.Color.from_rgb(255, 232, 239)

    await message.channel.send(embed=embed)


async def set_update_channel(message):
    pass


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


async def send_free_games(message):
    '''
    Gets data of the games which are currently free and sends
    it to the specified channel.

    Parameters
    ----------
    message - discord.Message
        Message containing the command.
    '''

    games = epicgames.get_free_games()

    for game in games:
        await message.channel.send(embed=get_game_embed(game))

COMMANDS = [
    MeowCommand('meow', 'replies with "meow".'),   
    MeowCommand('commands', "sends a list of the bot's commands.", send_commands),
    MeowCommand('help <command>', 'sends the description of the requested command.', send_help),
    MeowCommand('update', 'sends a list of the commands added in the last update, and the commands to be added in the upcoming update.', send_update),
    MeowCommand('set-update-channel', 'sets the channel the command was sent in as the channel for sending free games updates.', set_update_channel),
    MeowCommand('free', 'sends the games which are currently free on epic games.', send_free_games),
]

# Get bot token from file and run the bot.
with open('token.txt', 'r') as token_file:
    token = token_file.read()

client.run(token)