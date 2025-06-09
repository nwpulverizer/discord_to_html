import discord
from dotenv import load_dotenv
import os
import shutil
from pathlib import Path

from parseguild import (
    open_template,
    create_guild_directory,
    create_forum_list_item,
    write_guild_index,
    create_forum_directory,
    create_post_list_item,
    write_forum_index,
    create_post_directory,
    create_reply_item,
    write_post,
)
import argparse

# take command line arguments for where to write files
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--directory", help="directory to write files to")
parser.add_argument("-t", "--template", help="path to templates")

args = parser.parse_args()

write_path = Path(args.directory).resolve()
template_path = Path(args.template).resolve()
load_dotenv()
key = os.getenv("BOT_KEY")

intents = discord.Intents.none()
intents.message_content = True
intents.messages = True
intents.guilds = True


client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    forum_list_template_text = open_template(
        template_path.joinpath("forum-list-item.html")
    )
    post_template_text = open_template(template_path.joinpath("post.html"))
    reply_template_text = open_template(template_path.joinpath("reply.html"))
    post_list_item_text = open_template(template_path.joinpath("post-list-item.html"))
    for guild in client.guilds:
        guild_dir = create_guild_directory(guild, write_path)
        # Create css directory and copy style.css
        css_dir = guild_dir.joinpath("css")
        css_dir.mkdir(exist_ok=True)
        # Assuming style.css is directly in template_path
        shutil.copyfile(template_path.joinpath("style.css"), css_dir.joinpath("style.css"))
        forum_list_items = []
        for forum in guild.forums:
            forum_list_items.append(
                create_forum_list_item(forum, forum_list_template_text)
            )
            forum_dir = create_forum_directory(forum, guild_dir)
            post_list_items = []
            post_dir = create_post_directory(forum_dir)
            for post in forum.threads:
                post_list_items.append(create_post_list_item(post, post_list_item_text))
                replies = [reply async for reply in post.history()]
                reply_items = []
                for reply in replies:
                    reply_items.append(create_reply_item(reply, reply_template_text))
                write_post(post, reply_items, forum, post_template_text, post_dir)
            write_forum_index(
                forum,
                post_list_items,
                template_path.joinpath("forum-index.html"),
                forum_dir,
            )

        write_guild_index(
            guild,
            forum_list_items,
            Path(template_path).joinpath("guild-index.html"),
            guild_dir,
        )
    print("Done.")


client.run(key)
