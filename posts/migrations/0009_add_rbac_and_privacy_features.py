# Generated manually for adding RBAC and privacy features

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),  # Depends on your Django version
        ('posts', '0009_alter_post_author_alter_like_user_alter_comment_user_and_more'),  # Replace with your last migration
    ]

    operations = [
        # Add UserProfile model
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('admin', 'Administrator'), ('moderator', 'Moderator'), ('user', 'Regular User'), ('guest', 'Guest')], default='user', max_length=20)),
                ('bio', models.TextField(blank=True, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pictures/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='auth.user')),
            ],
        ),
        
        # Add privacy field to Post model
        migrations.AddField(
            model_name='post',
            name='privacy',
            field=models.CharField(
                choices=[('public', 'Public - Visible to everyone'), ('friends', 'Friends - Visible to friends only'), ('private', 'Private - Visible only to me')],
                default='public',
                max_length=10
            ),
        ),
    ]
