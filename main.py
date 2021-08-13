import os
import discord
import games
import asyncio
import datetime
import pytz
from discord.ext import tasks
from replit import db
from keep_alive import keep_alive

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
    'last': ['commands', 'help', 'update', 'set-update-channel', 'rating'],
    'upcoming': {
        'sale': 'sends a list of games which are currently on sale on different websites, like epic games, steam, origin, etc.',
        'sale <website>': 'sends a list of games which are currently on sale on the requested website.',
        'notify-sale <game-name>': 'sends a message when the requested game is on sale. also sends a private message to the user who ran the command.',
    }
}

GAME_NAME_ACRONYMS = {
    'lol': 'League of Legends',
    'cod': 'Call of Duty'
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

    elif message.content == 'woof':
        await message.channel.send('MEOW!')

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
    
    commands_str = '***last added commands:***\n\n'

    for command in UPDATE['last']:
        commands_str += '`meow {}`, '.format(command)

    commands_str = commands_str[:-2] # Remove last comma and space
    commands_str += '\n\n***upcoming commands:***\n\n'

    for name, description in UPDATE['upcoming'].items():
        commands_str += '`meow {}` - {}\n\n'.format(name, description)

    embed = discord.Embed()
    embed.set_thumbnail(url='https://i.pinimg.com/originals/56/7a/09/567a0964671de5b98b70583fe81ae5b0.gif')
    embed.color = discord.Color.from_rgb(255, 232, 239)
    embed.description = commands_str

    await message.channel.send(embed=embed)


async def set_update_channel(message):
    '''
    Sets the channel the command was sent in as the channel for
    sending free games updates by adding the channel id to the database.

    Parameters
    ----------
    message - discord.Message
        Message containing the command.
    '''

    if 'update channels' not in db.keys():
        db['update channels'] = {}
    
    db['update channels'][message.guild.id] = message.channel.id
    
    await message.channel.send('meow! channel successfully updated.') 


@tasks.loop(hours=24*7)
async def update_free_games():
    '''
    Sends a message to the update channel every time new games
    are available for free on Epic Games.
    '''

    channels_to_update = {}
    if 'update channels' in db.keys():
        channels_to_update = db['update channels'].values()

    for channel_id in channels_to_update:
        channel = client.get_channel(channel_id)
        await channel.send('meow! new games available for free:')
        await send_free_games(None, channel)


@update_free_games.before_loop
async def before_update_free_games():
    '''
    Waits until the first Thursday at 6 PM to start the update
    free games loop.
    '''

    await wait_until_time(games.THURSDAY)


@tasks.loop(hours=24*7)
async def remind_free_games():
    '''
    Sends a reminder to the update channel 24 hours before new games
    are available for free on Epic Games.
    '''

    channels_to_update = {}
    if 'update channels' in db.keys():
        channels_to_update = db['update channels'].values()

    for channel_id in channels_to_update:
        channel = client.get_channel(channel_id)
        await channel.send("meow! don't forget to get this week's free games:")
        await send_free_games(None, channel)


@remind_free_games.before_loop
async def before_remind_free_games():
    '''
    Waits until the first Wednesday at 6 PM to start the remind
    free games loop.
    '''

    await wait_until_time(games.WEDNESDAY)


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
    embed.color = discord.Color.from_rgb(255, 232, 239)

    return embed


async def send_free_games(message, channel=None):
    '''
    Gets data of the games which are currently free and sends
    it to the specified channel.

    Parameters
    ----------
    message - discord.Message
        Message containing the command.
    '''

    games_list = games.get_free_games()

    for game in games_list:
        if message is not None:
            await message.channel.send(embed=get_game_embed(game))
        elif channel is not None:
            await channel.send(embed=get_game_embed(game))


async def send_rating(message):
    '''
    Gets a game's rating and sends it to the channel.

    Parameters
    ----------
    message - discord.Message
        Message containing the command.
    '''

    embed = discord.Embed()
    embed.color = discord.Color.from_rgb(255, 232, 239)

    game_name = ' '.join(message.content.split()[2:]).lower()

    if game_name in GAME_NAME_ACRONYMS:
        game_name = GAME_NAME_ACRONYMS[game_name]

    try:
        game = games.get_rating(game_name)
    except games.GameNotFoundException as e:
        embed.set_thumbnail(url='https://lh6.googleusercontent.com/proxy/kdCQjGnPZzMTGOkwfVuecWA8KxN9iQZn9IVx85oI_Y-p3RsR2jRwUk0J3-_zwOpbZ4QEWi9RYZUOUVELKBzbc4EidWSNjzBiMVVn=w1200-h630-p-k-no-nu')
        embed.title = str(e)
    else:
        embed.title = game.get_name()
        embed.url = game.get_url()
        embed.set_image(url=game.get_image())
        embed.description = "the game's rating is **{}/100.**".format(game.get_rating())

    await message.channel.send(embed=embed)


async def send_sale(message):
    '''
    Sends a list of games which are currently on sale on different websites,
    like epic games, steam, origin, etc.

    Parameters
    ----------
    message - discord.Message
        Message containing the command.
    '''

    embed = discord.Embed()
    embed.color = discord.Color.from_rgb(255, 232, 239)

    num = message.content.split()[-1]
    
    if(num.isnumeric()):
        if(int(num) <= 15):
            games_dict = games.get_sale(int(num))
        else:
            games_dict = games.get_sale(15)
    else:
        games_dict = games.get_sale(5)

    for website, games_list in games_dict.items():
        await message.channel.send('**games on sale on {}:**'.format(website))
        
        for game in games_list:
            embed.title = game.get_name()
            embed.url = game.get_url()
            embed.set_thumbnail(url=game.get_image())
            embed.description = '~~{}~~  {}  **{}**'.format(game.get_original_price(), game.get_current_price(), game.get_discount_pct())

            await message.channel.send(embed=embed)


COMMANDS = [
    MeowCommand('meow', 'replies with "meow".'),   
    MeowCommand('commands', "sends a list of the bot's commands.", send_commands),
    MeowCommand('help <command>', 'sends the description of the requested command.', send_help),
    MeowCommand('update', 'sends a list of the commands added in the last update, and the commands to be added in the upcoming update.', send_update),
    MeowCommand('set-update-channel', 'sets the channel the command was sent in as the channel for sending free games updates.', set_update_channel),
    MeowCommand('free', 'sends the games which are currently free on epic games.', send_free_games),
    MeowCommand('rating <game-name>', 'sends the rating of the requested game, based on information from OpenCritic.', send_rating),
    MeowCommand('sale', 'sends a list of games which are currently on sale on different websites, like epic games, steam, origin, etc.', send_sale)
]

keep_alive()
client.run(os.environ['bot_token'])