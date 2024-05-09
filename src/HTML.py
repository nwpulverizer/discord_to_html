from pathlib import Path
from typing import ForwardRef, Optional, List
import markdown
import urllib.parse


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
            html.replace(
                "{{reply content}}", html_content + f"from {self.parent.title}"
            )
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
        channel: str,
        replies: List[Reply] = [],
    ):
        self.replies = replies
        self.title: str = title
        self.poster: str = username
        self.timestamp = timestamp
        self.id = id
        self.channel = channel
        self.thread_template = templates_path / "thread.html"
        self.post_card_template = templates_path / "threadcard.html"
        self.title = self.title.replace(" ", "-")

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
        self.thread_html = (
            thread_html.replace("{{Thread title}}", self.title)
            .replace("{{Thread replies}}", all_replies)
            .replace("{{Channel name}}", self.channel)
        )
        encoded_file_name = urllib.parse.quote_plus(f"{self.title}-{self.id}.html")
        self.thread_card_html = (
            card_html.replace("{{post-title}}", self.title)
            .replace("{{Username}}", str(self.poster))
            .replace("{{timestamp}}", self.timestamp.strftime("%c"))
            .replace(
                "{{thread page}}",
                urllib.parse.quote_plus(f"Posts/{self.title}-{self.id}.html"),
            )
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
        ).replace(
            "{{forum page}}", urllib.parse.quote_plus(f"/{self.title}/index.html")
        )


class Guild:
    def __init__(self, id: int, forums: List[Forum] = []):
        self.id = id
        self.forums = forums
        self.template = templates_path / "forumsindex.html"

    def to_html(self):
        all_forums = ""
        for forum in self.forums:
            forum.to_html()
            all_forums += forum.forum_card_html
        with open(self.template, "r") as f:
            self.html = f.read()
        self.html = self.html.replace("{{Forums}}", all_forums)

    def write_forums(self):
        pass
