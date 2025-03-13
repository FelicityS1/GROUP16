# urls.py in your posts app
from django.urls import path, re_path

# Import from post.py - these handle hex string IDs
from .post import (
    current_user, 
    get_posts, 
    create_post,
    like_post,
    comment_post,
    get_comments,
    delete_post
)

# Import from data.py
from . import data

# Import from views.py
from . import views

urlpatterns = [
    # Homepage
    path("", views.homepage, name="homepage"),
    
    # User Management
    path("users/", views.get_users, name="get_users"),
    path("create_user/", views.create_user, name="create_user"),
    path("login_user/", views.login_user, name="login_user"),
    path("update_user/<int:id>/", views.update_user, name="update_user"),
    path("delete_user/<int:id>/", views.delete_user, name="delete_user"),
    path("current_user/", current_user, name="current_user"),
    
    # Post routes
    path("api/posts/", get_posts, name="get_posts"),
    path("create_post/", create_post, name="create_post"),
    
    # Social action routes - using new pattern that matches frontend expectations
    path("<str:post_id>/like/", like_post, name="like_post"),
    path("<str:post_id>/comment/", comment_post, name="comment_post"),
    path("<str:post_id>/comments/", get_comments, name="get_comments"),
    path("<str:post_id>/delete/", delete_post, name="delete_post"),
    
    # Add the API pattern routes that your frontend is trying to access
    path("api/<str:post_id>/comments/", get_comments, name="api_get_comments"),
    path("api/<str:post_id>/comment/", comment_post, name="api_comment_post"),
    
    # Test endpoints
    path("test/", views.test_endpoint, name="test_endpoint"),
    path("test_json/", views.test_json, name="test_json"),
]