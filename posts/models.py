from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)  # User's unique username
    email = models.EmailField(unique=True) 
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the user was created


    def __str__(self):
        return self.usernamema

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey('User', on_delete=models.CASCADE)  # Assuming you have a User model
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
