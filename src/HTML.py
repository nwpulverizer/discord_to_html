from pathlib import Path
from re import L
from typing import ForwardRef, Optional, List
import markdown
import os


Post = ForwardRef("Post")
templates_path = Path("/home/nathan/Documents/boot.dev/discord_to_html/templates/")


class Reply:
    def __init__(self, content: str, username: str, parent: Post, timestamp, id: int):
        self.content = content
        self.username = username
        self.timestamp = timestamp
        self.parent = parent
        self.template = templates_path / "replycard.html"
        self.id = id

    def to_html(self):
        with open(self.template, "r") as f:
            html = f.read()
        html_content = markdown.markdown(self.content)
        self.html = (
            html.replace("{{reply content}}", html_content)
            .replace("{{Username}}", str(self.username))
            .replace("{{timestamp}}", self.timestamp.strftime("%c"))
        )


class Post:
    def __init__(
        self,
        title: str,
        username: str,
        timestamp,
        id: int,
        replies: List[Reply] = [],
    ):
        self.replies = replies
        self.title: str = title
        self.poster: str = username
        self.timestamp = timestamp
        self.id = id
        self.thread_template = templates_path / "thread.html"
        self.post_card_template = templates_path / "threadcard.html"

    # How can I make sure these are sorted by time?
    def to_html(self):
        with open(self.thread_template, "r") as f:
            thread_html = f.read()
        with open(self.post_card_template, "r") as f:
            card_html = f.read()
        all_replies = ""
        if self.replies is not []:
            for reply in sorted(self.replies, key=lambda x: x.timestamp):
                reply.to_html()
                all_replies += reply.html
        else:
            print("No replies.")
        self.thread_html = thread_html.replace("{{Thread title}}", self.title).replace(
            "{{Thread replies}}", all_replies
        )
        self.thread_card_html = (
            card_html.replace("{{post-title}}", self.title)
            .replace("{{Username}}", str(self.poster))
            .replace("{{timestamp}}", self.timestamp.strftime("%c"))
            .replace("{{thread page}}", f"Posts/{self.title}-{self.id}.html")
        )


class Forum:
    def __init__(self, id: int, posts: List[Post] = [], title: Optional[str] = None):
        self.id = id
        self.posts = posts
        self.title = title
        self.forum_template = templates_path / "forum.html"
        self.forum_card_template = templates_path / "forumcard.html"

    def to_html(self):
        if self.title is None:
            raise ValueError("Title must not be None")
        with open(self.forum_template, "r") as f:
            forum_html = f.read()
        all_posts = ""
        if self.posts is not []:
            for post in sorted(self.posts, key=lambda x: x.timestamp):
                post.to_html()
                all_posts += post.thread_card_html
        else:
            print(f"No Posts. in {self.title}")
        self.forum_html = forum_html.replace("{{Channel name}}", self.title).replace(
            "{{Threads}}", all_posts
        )
        with open(self.forum_card_template, "r") as f:
            forum_card_html = f.read()
        self.forum_card_html = forum_card_html.replace(
            "{{forum-name}}", self.title
        ).replace("{{forum page}}", f"/{self.title}/")


class Guild:
    def __init__(self, id: int, forums: List[Forum] = []):
        self.id = id
        self.forums = forums

    def to_html(self):
        for forum in self.forums:
            forum.to_html()
        # TODO: create channel index

    def write_forums(self):
        pass


public_path = Path("/home/nathanp/Documents/boot.dev/discord_html/public/")


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
    guild_path = public_path / str(guild.id)
    os.mkdir(guild_path)
    for forum in guild.forums:
        # make the forums folder
        if forum.title is not None:
            forum_path = guild_path / forum.title
            os.mkdir(forum_path)
        else:
            raise ValueError("Forum needs a title to be written.")

        # write the index.html to the folder for the forum
        with open(forum_path / "index.html", "w") as f:
            f.write(forum.forum_html)
        # make the posts folder for the forum
        posts_path = forum_path / "Posts"
        os.mkdir(posts_path)
        # write the posts to the folder
        for post in forum.posts:
            post_path = posts_path / f"{post.title}-{post.id}.html"
            with open(post_path, "w") as f:
                try:
                    f.write(post.thread_html)
                except ValueError:
                    raise ValueError(
                        f"post {post.title} does not have html generated yet."
                    )

    # TODO: make folder structure. Do I do that here? Another function?


# QUESTION: is it worth pulling this into another function?
# now I am repeating the same for loops again as in the make_dir_structure
def error_if_dir_not_exist(dir: Path):
    if not os.path.isdir(dir):
        raise OSError(f"The directory {dir} has not been created")


def write_files(public_path: Path, guild: Guild):
    guild_path = public_path / str(guild.id)
    error_if_dir_not_exist(guild_path)
    for forum in guild.forums:
        forum_path = guild_path / forum.title
        error_if_dir_not_exist(forum_path)
        with open(forum_path / "index.html", "w") as f:
            f.write(forum.forum_html)
        post_path = forum_path / "Posts"
        if not os.path.isdir(post_path):
            for post in forum.posts:
                error_if_dir_not_exist(post_path)
                post_path = post_path / f"{post.title}-{post.id}.html"
                with open(post_path, "w") as f:
                    try:
                        f.write(post.thread_html)
                    except ValueError:
                        raise ValueError(
                            f"{post.title} in {forum.title} does not have html generated yet."
                        )
