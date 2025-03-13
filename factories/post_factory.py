# Fixed post_factory.py to avoid circular imports
from django.contrib.auth import get_user_model
from django.apps import apps

class PostFactory:
    @staticmethod
    def create_post(post_type, title, content, metadata, author=None):
        # Get the Post model dynamically to avoid circular imports
        Post = apps.get_model('posts', 'Post')
        User = get_user_model()
        
        # Check if the author exists when required
        if not author:
            author = None  # This allows the post to be created without an author
        elif author and not isinstance(author, User):
            # If author is provided but not a User instance, try to get the actual user
            if hasattr(author, 'pk'):
                # If it's a SimpleLazyObject or similar with a pk
                try:
                    author = User.objects.get(pk=author.pk)
                except Exception:
                    author = None
            else:
                author = None
        
        post = Post.objects.create(
            post_type=post_type,
            title=title,
            content=content,
            metadata=metadata,
            author=author  # Now author is handled properly
        )
        return post