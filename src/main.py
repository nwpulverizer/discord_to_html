import discord
from discord.ext import commands
from discord import app_commands # Added
from dotenv import load_dotenv
import os
import shutil
from pathlib import Path
from typing import Union # Added for type hinting

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

# Make paths global for now, will be refactored in Step 4
write_path = Path(args.directory).resolve()
template_path = Path(args.template).resolve()
load_dotenv()
key = os.getenv("BOT_KEY")

intents = discord.Intents.default() # Using default intents
intents.message_content = True # Explicitly enable if needed
intents.guilds = True
# intents.messages = True # Keep if text commands need this
intents.guilds = True   # Keep

# Replace discord.Client with commands.Bot
bot = commands.Bot(command_prefix="!", intents=intents) # Changed

# The global template loading was already commented out, which is fine.
# These will be loaded or accessed by command functions as needed.
# forum_list_template_text = open_template(
#     template_path.joinpath("forum-list-item.html")
# )
# post_template_text = open_template(template_path.joinpath("post.html"))
# reply_template_text = open_template(template_path.joinpath("reply.html"))
# Pre-load templates globally (temporary measure for this step)
try:
    forum_list_template_text_global = open_template(template_path.joinpath("forum-list-item.html"))
    post_template_text_global = open_template(template_path.joinpath("post.html"))
    reply_template_text_global = open_template(template_path.joinpath("reply.html"))
    post_list_item_text_global = open_template(template_path.joinpath("post-list-item.html"))
    guild_index_template_path_global = template_path.joinpath("guild-index.html")
    forum_index_template_path_global = template_path.joinpath("forum-index.html")
except FileNotFoundError as e:
    print(f"Critical Error: One or more template files not found in {template_path}. Bot cannot start. Details: {e}")
    exit() # Exit if templates are missing, as the bot's core function depends on them.
except Exception as e:
    print(f"Critical Error during template loading: {e}. Bot cannot start.")
    exit()

# Helper function to process a single forum channel
async def _process_forum_channel(forum_channel: discord.ForumChannel, guild_dir: Path, template_path_root: Path, interaction: Union[discord.Interaction, None] = None):
    if interaction:
        await interaction.followup.send(f"Processing forum: {forum_channel.name}...", ephemeral=True)

    forum_dir = create_forum_directory(forum_channel, guild_dir)
    post_list_items = []
    post_dir = create_post_directory(forum_dir)

    threads_to_process = []
    try:
        active_threads = list(forum_channel.threads) # Make it a list
        archived_threads_list = []
        async for thread in forum_channel.archived_threads(limit=None):
             archived_threads_list.append(thread)
        threads_to_process = active_threads + archived_threads_list
    except discord.Forbidden:
        if interaction: await interaction.followup.send(f"Permissions error fetching threads for {forum_channel.name}.", ephemeral=True)
        raise
    except Exception as e:
        if interaction: await interaction.followup.send(f"Error fetching threads for {forum_channel.name}: {e}", ephemeral=True)
        raise

    for post_thread in threads_to_process:
        post_list_items.append(create_post_list_item(post_thread, post_list_item_text_global))
        replies_data = []
        try:
            async for message in post_thread.history(limit=None):
                reply_item_html, timestamp = create_reply_item(message, reply_template_text_global)
                replies_data.append((reply_item_html, timestamp))
        except discord.Forbidden:
            if interaction: await interaction.followup.send(f"Permissions error fetching messages in thread {post_thread.name}. Some messages may be missing.", ephemeral=True)
        except Exception as e:
            if interaction: await interaction.followup.send(f"Error fetching messages for thread {post_thread.name}: {e}. Some messages may be missing.", ephemeral=True)

        write_post(post_thread, replies_data, forum_channel, post_template_text_global, post_dir)

    write_forum_index(
        forum_channel,
        post_list_items,
        forum_index_template_path_global,
        forum_dir,
    )
    if interaction:
        await interaction.followup.send(f"Finished processing forum: {forum_channel.name}.", ephemeral=True)

# Helper function to process an entire guild
async def _process_guild(guild: discord.Guild, write_path_base: Path, template_path_root: Path, interaction: Union[discord.Interaction, None] = None):
    guild_dir = create_guild_directory(guild, write_path_base)

    css_dir = guild_dir.joinpath("css")
    css_dir.mkdir(exist_ok=True)
    shutil.copyfile(template_path_root.joinpath("style.css"), css_dir.joinpath("style.css"))

    forum_list_items_html = []
    for forum in guild.forums:
        try:
            await _process_forum_channel(forum, guild_dir, template_path_root, interaction)
            forum_list_items_html.append(
                create_forum_list_item(forum, forum_list_template_text_global)
            )
        except discord.Forbidden:
            if interaction: await interaction.followup.send(f"Skipping forum {forum.name} due to permissions error.", ephemeral=True)
        except Exception as e:
            if interaction: await interaction.followup.send(f"Skipping forum {forum.name} due to an error: {e}", ephemeral=True)
            print(f"Error processing forum {forum.name} in guild {guild.name}: {e}")

    write_guild_index(
        guild,
        forum_list_items_html,
        guild_index_template_path_global,
        guild_dir,
    )

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    print(f"Serving from: {write_path}")
    print(f"Using templates from: {template_path}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.tree.command(name="archive_all_forums", description="Archives all forum channels in this server.")
@app_commands.checks.has_permissions(administrator=True)
async def archive_all_forums(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    guild = interaction.guild
    if not guild:
        await interaction.followup.send("This command can only be used in a server.", ephemeral=True)
        return

    if not write_path or not template_path:
        await interaction.followup.send("Error: Output directory or template path not configured.", ephemeral=True)
        return
    if 'forum_list_template_text_global' not in globals():
        await interaction.followup.send("Error: Templates not loaded. Check bot console.", ephemeral=True)
        return

    await interaction.followup.send(f"Starting archival process for server: {guild.name}...")
    try:
        await _process_guild(guild, write_path, template_path, interaction)
        guild_output_dir = write_path.joinpath(f"public-{guild.id}")
        await interaction.followup.send(f"Successfully archived all forum channels for {guild.name}. Files are in {guild_output_dir}")
    except discord.Forbidden:
        await interaction.followup.send("Error: Bot is missing critical permissions. Archival may be incomplete.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"An unexpected error occurred during full guild archival: {e}", ephemeral=True)
        print(f"Error in archive_all_forums command: {e}")

@archive_all_forums.error
async def archive_all_forums_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.followup.send("You don't have permission to use this command (Administrator required).", ephemeral=True)
    elif interaction.response.is_done():
        await interaction.followup.send(f"An error occurred: {error}", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)
    print(f"Error in archive_all_forums_error handler: {error}")


@bot.tree.command(name="archive_forum", description="Archives a specific forum channel in this server.")
@app_commands.describe(forum_channel="The forum channel to archive.")
@app_commands.checks.has_permissions(administrator=True)
async def archive_forum(interaction: discord.Interaction, forum_channel: discord.ForumChannel):
    await interaction.response.defer(ephemeral=False)
    guild = interaction.guild
    if not guild:
        await interaction.followup.send("Error: Guild context not found.", ephemeral=True)
        return

    if not write_path or not template_path:
        await interaction.followup.send("Error: Output directory or template path not configured.", ephemeral=True)
        return
    if 'forum_list_template_text_global' not in globals():
        await interaction.followup.send("Error: Templates not loaded. Check bot console.", ephemeral=True)
        return

    guild_dir = write_path.joinpath(f"public-{guild.id}/")
    guild_dir.mkdir(exist_ok=True)
    css_dir = guild_dir.joinpath("css")
    css_dir.mkdir(exist_ok=True)
    shutil.copyfile(template_path.joinpath("style.css"), css_dir.joinpath("style.css"))

    await interaction.followup.send(f"Starting archival process for forum: {forum_channel.name} in server {guild.name}...")
    try:
        await _process_forum_channel(forum_channel, guild_dir, template_path, interaction)
        forum_output_dir = guild_dir.joinpath(f"{forum_channel.name}-{forum_channel.id}")
        await interaction.followup.send(f"Successfully archived forum: {forum_channel.name}. Files are in {forum_output_dir}")
    except discord.Forbidden:
        await interaction.followup.send(f"Permissions error while processing {forum_channel.name}. Archival may be incomplete.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"An unexpected error occurred for forum {forum_channel.name}: {e}", ephemeral=True)
        print(f"Error in archive_forum command for {forum_channel.name}: {e}")

@archive_forum.error
async def archive_forum_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    # Error handling logic remains the same as provided in the prompt
    if isinstance(error, app_commands.MissingPermissions):
        if interaction.response.is_done():
            await interaction.followup.send("You don't have permission to use this command (Administrator required).", ephemeral=True)
        else:
            await interaction.response.send_message("You don't have permission to use this command (Administrator required).", ephemeral=True)
    elif isinstance(error, app_commands.CommandInvokeError) and isinstance(error.original, discord.Forbidden):
        if interaction.response.is_done():
            await interaction.followup.send("The bot encountered a permissions error trying to access channel/message data.",ephemeral=True)
        else:
            await interaction.response.send_message("The bot encountered a permissions error trying to access channel/message data.",ephemeral=True)
    else:
        if interaction.response.is_done():
            await interaction.followup.send(f"An error occurred with the command: {error}",ephemeral=True)
        else:
            await interaction.response.send_message(f"An error occurred with the command: {error}", ephemeral=True)
    print(f"Error in archive_forum_error handler: {error}")

bot.run(key)
