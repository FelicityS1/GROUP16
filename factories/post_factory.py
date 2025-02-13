# Inside post_factory.py
from posts.models import Post, User

class PostFactory:
    @staticmethod
    def create_post(post_type, title, content, metadata, author=None):  # Default author to None
        # Check if the author exists when required
        if not author:
            author = None  # This allows the post to be created without an author
        else:
            if not isinstance(author, User):
                raise ValueError("Author must be a User instance")

        post = Post.objects.create(
            post_type=post_type,
            title=title,
            content=content,
            metadata=metadata,
            author=author  # Now author is optional
        )
        return post


