from HTML import Guild
from pathlib import Path
import os
import shutil
import urllib.parse


# TODO: I should take the file creation logic out of here
# this function should ONLY create the directory structure.
# file creation should happen as a method for each class so that I can make the directory structure
# and then write to it. How I have it now, I still need to make the links to indivudal posts in the forums page
# (replace {thread link} in template or whatever) but I have no guarantee that the file is there.
def make_dir_structure(public_path: Path, guild: Guild):
    # what is required to make the dir structure? any info
    # at all about the guild?
    # I do need a name if I am doing this for many guilds or ID.
    # If I am naming the forum path I need the forum names
    # IF I am not naming the forum path the same as the forum title,
    # then I do not need names, but I guess I will need some way to
    # put the corresponding forums in the correct dir.
    # ie which one is /forum1 which is /forum2 if I name them generically like
    # that.

    # make the guild's folder
    guild_path = public_path / str(guild.id)
    # Remove structure if it already exists.
    if os.path.exists(guild_path):
        shutil.rmtree(guild_path)
    os.mkdir(guild_path)
    for forum in guild.forums:
        # make the forums folder
        if forum.title is not None:
            forum_path = guild_path / forum.title
            os.mkdir(forum_path)
        else:
            raise ValueError("Forum needs a title to be written.")
        # make the posts folder for the forum
        posts_path = forum_path / "Posts"
        os.mkdir(posts_path)

    # TODO: make folder structure. Do I do that here? Another function?


# QUESTION: is it worth pulling this into another function?
# now I am repeating the same for loops again as in the make_dir_structure
def error_if_dir_not_exist(dir: Path):
    if not os.path.isdir(dir):
        raise OSError(f"The directory {dir} has not been created")


def write_files(public_path: Path, guild: Guild):
    guild_path = public_path / str(guild.id)
    error_if_dir_not_exist(guild_path)
    with open(guild_path / "index.html", "w") as f:
        f.write(guild.html)
    for forum in guild.forums:
        forum_path = guild_path / urllib.parse.quote_plus(forum.title)
        error_if_dir_not_exist(forum_path)
        with open(forum_path / "index.html", "w") as f:
            f.write(forum.forum_html)
        post_path = forum_path / "Posts"
        error_if_dir_not_exist(post_path)
        for post in forum.posts:
            this_post_path = post_path / f"{post.title}-{post.id}.html"
            with open(this_post_path, "w") as f:
                try:
                    f.write(post.thread_html)
                except ValueError:
                    raise ValueError(
                        f"{post.title} in {forum.title} does not have html generated yet."
                    )
