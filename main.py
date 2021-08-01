import discord
import epicgames

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == 'meow':
        await message.channel.send('meow')

    if message.content == 'meow free':
        games = epicgames.get_free_games()

        for game in games:
            embed = discord.Embed()
            embed.title = game.get_name()
            embed.url = game.get_url()
            embed.set_image(url=game.get_image())
            await message.channel.send(embed=embed)

# Get bot token from file and run the bot
with open('token.txt', 'r') as token_file:
    token = token_file.read()

client.run(token)