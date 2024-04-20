from pathlib import Path
from typing import ForwardRef, Optional, List
import markdown


Post = ForwardRef("Post")


class Reply:
    def __init__(self, content: str, username: str, parent: Post, timestamp):
        self.content = content
        self.username = username
        self.timestamp = timestamp
        self.parent = parent
        self.template = Path("../templates/replycard.html")

    def to_html(self):
        with open(self.template, "r") as f:
            html = f.read()
        html_content = markdown.markdown(self.content)
        self.html = (
            html.replace("{{reply content}}", html_content)
            .replace("{{Username}}", self.username)
            .replace("{{timestamp}}", self.timestamp)
        )


class Post:
    def __init__(
        self, replies: List, title: str, username: str, content: str, timestamp
    ):
        self.replies = replies
        self.title: str = title
        self.poster: str = username
        self.timestamp = timestamp
        self.content: str = content
        self.template = Path("../templates/thread.html")

    # How can I make sure these are sorted by time?
    def to_html(self):
        with open(self.template, "r") as f:
            html = f.read()
        html_content = markdown.markdown(self.content)
        all_replies = ""
        for reply in self.replies:
            reply.to_html()
            all_replies += reply.html
        self.html = (
            html.replace("{{Thread title}}", self.title)
            .replace("{{Thread content}}", html_content)
            .replace("{{Thread replies}}", all_replies)
        )


class Forum:
    def __init__(self, posts: Optional[List[Post]] = None, title: Optional[str] = None):
        self.posts: Optional[List[Post]] = posts
        self.title: Optional[str] = title


class Guild:
    def __init__(self, forums: List[Forum]):
        self.forums = forums
