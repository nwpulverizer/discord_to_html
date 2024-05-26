import shutil
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

import discord
import markdown


def open_template(template_path: Path) -> str:
    with open(template_path) as f:
        return f.read()


def create_guild_directory(guild: discord.Guild, write_path: Path) -> Path:
    """
    Creates the guild directory only.
    Will first delete the directory if it already exists as well as its contents.
    Should be of the form write_path/public-{guild-id}/
    """
    guild_dir = write_path.joinpath(f"public-{guild.id}/")
    shutil.rmtree(guild_dir, ignore_errors=True)
    guild_dir.mkdir()
    return guild_dir


def create_forum_list_item(forum: discord.ForumChannel, template_text: str) -> str:
    """
    Creates a list item to go into the guild-index.html file and returns the string html.
    Eventually, this will be appended to the guild-index.html file to replace the {{Forums}}
    placeholder in the template.
    """
    # path relative to guild directory should work?
    list_item = template_text.replace(
        "{{Forum Link}}", f"./{forum.name}-{forum.id}/index.html"
    ).replace("{{Forum Title}}", forum.name)
    return list_item


def write_guild_index(
    guild: discord.Guild,
    forum_list: List[str],
    template_path: Path,
    write_path: Path,
) -> None:
    """
    Fills in the guild-index.html file to approproate directory.
    This file provides links to the forums in a discord server.
    forum_list should be a list of strings of html forum list items.
    These forum list items should come from forum-list-item.html template.
    """
    guild_index_path = write_path.joinpath("index.html")
    shutil.copyfile(template_path, guild_index_path)
    with open(guild_index_path, "r+") as f:
        html = f.read()
        html = html.replace("{{Guild Title}}", guild.name).replace(
            "{{Forums}}", "".join(forum_list)
        )
        # move to starting position of file to overwrite.
        f.seek(0)
        f.write(html)
        f.truncate()


def create_forum_directory(forum: discord.ForumChannel, write_path: Path) -> Path:
    """
    Creates the directory for a given forum.
    The write path should be the guild directory created and returned from the create_guild_directory function
    """
    forum_dir = write_path.joinpath(f"{forum.name}-{forum.id}/")
    forum_dir.mkdir()
    return forum_dir


def create_post_list_item(post: discord.Thread, template_text: str) -> str:
    """
    Creates a list item to go into the forum-index.html file and returns the string html.
    Eventually, this will be appended to the forum-index.html file to replace the {{Posts}}
    placeholder in the template.
    """
    list_item = (
        template_text.replace("{{Post Link}}", f"./Posts/{post.id}.html")
        .replace("{{Post Title}}", post.name)
        .replace("{{User}}", "user" + str(hash(post.owner)))
        .replace("{{Timestamp}}", str(post.created_at))
    )
    return list_item


def write_forum_index(
    forum: discord.ForumChannel,
    posts_list: List[str],
    template_path: Path,
    write_path: Path,
) -> None:
    """
    Fills in the forum-index.html template file to appropriate directory.
    This file provides links to the posts in a forum.
    posts_list should be a list of strings of html post list items.
    These should come from filling in the post-list-item.html template.
    """
    forum_index_path = write_path.joinpath("index.html")
    shutil.copyfile(template_path, forum_index_path)
    with open(forum_index_path, "r+") as f:
        html = f.read()
        html = (
            html.replace("{{Forum Title}}", forum.name)
            .replace("{{Guild Link}}", "../index.html")
            .replace("{{Posts}}", "".join(posts_list))
        )
        f.seek(0)
        f.write(html)
        f.truncate()


def create_post_directory(forum_path: Path) -> Path:
    """
    creates the posts directory for a forum. Expects the forum path
    from the create_forum_directory function.
    """
    post_path = forum_path.joinpath("Posts/")
    post_path.mkdir()
    return post_path


def create_reply_item(
    reply: discord.Message, template_text: str
) -> Tuple[str, datetime]:
    """
    creates the individual reply from the reply.html template text.
    Will be put into post.html once all the replies are aggregated.
    Timestamp also return for sorting.
    """
    timestamp = reply.created_at
    reply_item = (
        template_text.replace("{{Timestamp}}", str(reply.created_at))
        .replace("{{User}}", "user" + str(hash(reply.author)))
        .replace("{{Content}}", markdown.markdown(reply.content))
    )

    return reply_item, timestamp


def write_post(
    post: discord.Thread,
    reply_list: List[str],
    forum: discord.ForumChannel,
    template_text: str,
    write_path: Path,
) -> None:
    """
    Fills in the post.html file and writes to appropriate directory.
    Since there will likely be many posts hitting the same template,
    instead of passing the template path like other write_ functions, we
    pass the template_text as to not keep hitting disk for the same template.
    """
    sorted_replies_by_date = sorted(reply_list, key=lambda x: x[1])
    reply_only = [i[0] for i in sorted_replies_by_date]

    post_file_path = write_path.joinpath(f"{post.id}.html")
    file_text = (
        template_text.replace("{{Forum Link}}", "../index.html")
        .replace("{{Forum Title}}", forum.name)
        .replace("{{Post Title}}", post.name)
        .replace("{{Replies}}", "".join(reply_only))
    )
    with open(post_file_path, "w") as f:
        f.write(file_text)
