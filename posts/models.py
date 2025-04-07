from django.db import models
from django.contrib.auth.models import User
import uuid

class Post(models.Model):
    """
    Post model with privacy settings
    """
    PRIVACY_CHOICES = [
        ('public', 'Public - Visible to everyone'),
        ('friends', 'Friends - Visible to friends only'),
        ('private', 'Private - Visible only to me')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts", null=True)
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    post_type = models.CharField(max_length=10, choices=[('text', 'Text'), ('image', 'Image')], default='text')
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='public')
    metadata = models.JSONField(blank=True, null=True)
    
    def like_count(self):
        return self.likes.count()
    
    def comment_count(self):
        return self.comments.count()
    
    def is_visible_to(self, user):
        """
        Determine if this post is visible to a specific user
        """
        # Public posts are visible to everyone
        if self.privacy == 'public':
            return True
            
        # Anonymous users can only see public posts
        if not user.is_authenticated:
            return False
            
        # Post authors can always see their own posts
        if self.author == user:
            return True
            
        # Admins and moderators can see all posts
        if hasattr(user, 'profile') and user.profile.role in ['admin', 'moderator']:
            return True
            
        # For friends-only posts, we'd check if the user is a friend
        if self.privacy == 'friends':
            # This is where you'd implement friend relationship checking
            # For now, we're just returning False as the friend system isn't implemented
            return False
            
        # Private posts are only visible to the author (and admins/mods, handled above)
        if self.privacy == 'private':
            return False
            
        # Default to not visible
        return False
    
    def __str__(self):
        return f"{self.author.username}: {self.content[:30]}"

class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')  # Prevent duplicate likes
    
    def __str__(self):
        return f"{self.user.username} liked {self.post.id}"

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} commented on {self.post.id}"