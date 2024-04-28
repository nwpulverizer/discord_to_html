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
    guilds = []
    for guild in client.guilds:
        this_guild = Guild(guild.id)
        print(this_guild.id)
        for forum in guild.forums:
            this_forum = Forum(title=forum.name, id=forum.id)
            for thread in forum.threads:
                messages = [message async for message in thread.history()]
                this_post = Post(
                    thread.name, str(thread.owner), thread.created_at, thread.id
                )
                this_forum.posts.append(this_post)
                for message in messages:
                    reply = Reply(
                        message.content,
                        message.author,
                        this_post,
                        message.created_at,
                        message.id,
                    )
                    this_post.replies.append(reply)
        this_guild.forums.append(this_forum)
        guilds.append(this_guild)


client.run(key)
