import discord
from dotenv import load_dotenv
import os
from pathlib import Path
from HTML import Reply, Post, Forum, Guild
from io_handlers import make_dir_structure, write_files

public_path = Path("../public/").resolve()
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
        for forum in guild.forums:
            this_forum = Forum(title=forum.name, id=forum.id)
            for thread in forum.threads:
                this_post = Post(
                    thread.name,
                    str(thread.owner),
                    thread.created_at,
                    thread.id,
                    this_forum.title,
                    [],
                )
                messages = [message async for message in thread.history()]
                for message in messages:

                    reply = Reply(
                        message.content,
                        message.author,
                        this_post,
                        message.created_at,
                        message.id,
                    )
                    this_post.replies.append(reply)
                this_forum.posts.append(this_post)
        this_guild.forums.append(this_forum)
        guilds.append(this_guild)
    for guild in guilds:
        guild.to_html()
        make_dir_structure(public_path, guild)
        write_files(public_path, guild)


client.run(key)
