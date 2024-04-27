import discord
from dotenv import load_dotenv
import os
from HTML import Reply, Post, Forum, Guild

load_dotenv()
key = os.getenv("BOT_KEY")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    for guild in client.guilds:
        this_guild = Guild()
        for forum in guild.forums:
            this_forum = Forum(
                title=forum.name,
            )
            for thread in forum.threads:
                # I don't really know what starter message is. It's not the
                # Thing you put in when you create your thread
                messages = [message async for message in thread.history()]
                this_post = Post(thread.name, str(thread.owner), thread.created_at)
                this_forum.posts.append(this_post)
                for message in messages:
                    reply = Reply(
                        message.content, message.author, this_post, message.created_at
                    )
                    this_post.replies.append(reply)
            this_forum.to_html()


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
