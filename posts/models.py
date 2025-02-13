from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)  # User's unique username
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the user was created

    def __str__(self):
        return self.username  # Fix typo: "usernamema" -> "username"

class Post(models.Model):
    # Define post types
    POST_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
        # Add more post types as needed
    )

    title = models.CharField(max_length=200)
    content = models.TextField()
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='image')  # Set default to 'image'
    author = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True)  # Allow NULL for author
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)  # Add metadata field as JSONField

    def __str__(self):
        return self.title

