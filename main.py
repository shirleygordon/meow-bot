import discord

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

# Get bot token from file and run the bot
with open('token.txt', 'r') as token_file:
    token = token_file.read()

client.run(token)