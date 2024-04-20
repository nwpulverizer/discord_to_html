import discord
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv("BOT_KEY")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    for guild in client.guilds:
        for forum in guild.forums:
            for thread in forum.threads:
                messages = [message async for message in thread.history()]
                for message in messages:
                    print(message.content)


# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return
#
#     if message.content.startswith("$hello"):
#         await message.channel.send("Hello!")
#         for guild in client.guilds:
#             await get_forums(guild)
#

client.run(key)
