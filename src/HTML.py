from pathlib import Path
from typing import ForwardRef, Optional, List
import markdown


Post = ForwardRef("Post")
templates_path = Path("/home/nathan/Documents/boot.dev/discord_to_html/templates/")


class Reply:
    def __init__(self, content: str, username: str, parent: Post, timestamp):
        self.content = content
        self.username = username
        self.timestamp = timestamp
        self.parent = parent
        self.template = templates_path / "replycard.html"

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
        replies: List[Reply] = [],
    ):
        self.replies = replies
        self.title: str = title
        self.poster: str = username
        self.timestamp = timestamp
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
            # TODO: Replace {{thread page}} with correct href in template.
            # must decide naming for threads.
        )


class Forum:
    def __init__(self, posts: List[Post] = [], title: Optional[str] = None):
        self.posts = posts
        self.title = title
        self.template = templates_path / "channel.html"

    def to_html(self):
        with open(self.template, "r") as f:
            html = f.read()
        all_posts = ""
        if self.posts is not []:
            for post in sorted(self.posts, key=lambda x: x.timestamp):
                post.to_html()
                all_posts += post.thread_card_html
        else:
            print(f"No Posts. in {self.title}")
        self.html = html.replace("{{Channel name}}", self.title).replace(
            "{{Threads}}", all_posts
        )


class Guild:
    def __init__(self, forums: List[Forum] = []):
        self.forums = forums
