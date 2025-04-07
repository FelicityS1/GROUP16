from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=[
        ('user', 'Regular User'),
        ('admin', 'Administrator'),
        ('moderator', 'Moderator'),
        ('guest', 'Guest')
    ], default='user')

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_moderator(self):
        return self.role == 'moderator'
    
    def is_regular_user(self):
        return self.role == 'user'
    
    def is_guest(self):
        return self.role == 'guest'
    
    def can_delete_any_post(self):
        return self.role in ['admin', 'moderator']
    
    def can_delete_any_comment(self):
        return self.role in ['admin', 'moderator']
    
    def can_edit_user_profiles(self):
        return self.role == 'admin'


# Signal to create a user profile whenever a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    instance.profile.save()