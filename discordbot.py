import discord
from discord.ext import commands
import requests
import json

with open('config.json') as config_file:
    data = json.load(config_file)

TOKEN = data['TOKEN']
ALLGEMEIN_ID = data['ALLGEMEIN_ID']
OOF_ID = data['OOF_ID']
GIF_ID = data['GIF_ID']
BLOCKED_IDS = data['BLOCKED_IDS']
ALLOWED_ROLE_ID = data['ALLOWED_ROLE_ID']
LOG_CHANNEL_ID = data['LOG_CHANNEL_ID']
MUSIC_CHANNEL_ID = data['MUSIC_CHANNEL_ID']

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix='?', intents=intents)


#VC-limit for DC as a public-command
@client.command()
async def limit(ctx, limit: int):
    
    channel_id = ctx.channel.id
    if (limit >= 99 or limit < 2):
        await ctx.channel.send('Das Limit muss zwischen 2 & 99 liegen!')
        return 
    if channel_id in BLOCKED_IDS:
        await ctx.channel.send('Das ist für diesen Voicechannel nicht gewünscht!')
        return
    if not ctx.author.voice:
        await ctx.channel.send('Du bist nicht in einem VoiceChannel!')
        return
    if channel_id != ctx.author.voice.channel.id:
        await ctx.channel.send('Du bist nicht in dem dazugehörigen VoiceChannel!')
    else:
        await ctx.author.voice.channel.edit(user_limit=limit)
        await ctx.channel.send(f'Das Benutzerlimit für den Kanal {ctx.author.voice.channel.name} wurde auf {limit} gesetzt')

#clear-command for serverteam
@client.command()
async def clear(ctx, amount=1):

    channel = ctx.message.channel
    messages = []
    for role in ctx.message.author.roles:
        if role.id in ALLOWED_ROLE_ID:
            async for message in channel.history(limit=amount):
                messages.append(message)
            await channel.delete_messages(messages)
            #await log_channel.send(" "+ str(amount) +" Nachrichten wurden im Channel "+ message.channel.name +" gelöscht.")
            break

#Cchatfilter for special channels
@client.event
async def on_message(message):
    await client.process_commands(message)
    
    if message.channel.id == OOF_ID and message.content != "oof":
        await message.delete()
        return

    if message.channel.id == GIF_ID:
        if message.content and not message.content.startswith("https://tenor.com/"):
            await message.delete()
            return

        if message.attachments:
            for attachment in message.attachments:
                if not attachment.url.startswith("https://tenor.com/"):
                    await message.delete()
                    return
                
#deleted-message-log without "?clear"-delete
@client.event                
async def on_message_delete(message):

    await client.process_commands(message)

    if message.content.startswith('?clear'):
        return

    allowed_role_found = False
    for role in message.author.roles:
        if role.id in ALLOWED_ROLE_ID:
            
            if message.channel.id == MUSIC_CHANNEL_ID:
                return
            else:
                allowed_role_found = True
                log_channel = client.get_channel(LOG_CHANNEL_ID)
                await log_channel.send('Eine **Teamnachricht** wurde aus dem **'+ message.channel.name +'** gelöscht.')
                break

    if not allowed_role_found:
        log_channel = client.get_channel(LOG_CHANNEL_ID)
        await log_channel.send('Die Nachricht "**'+ message.content +'**" von **'+ message.author.name +'** wurde aus dem **'+ message.channel.name +'** gelöscht.')   
          
client.run(TOKEN)