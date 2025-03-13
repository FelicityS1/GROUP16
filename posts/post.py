import json
import os
import uuid
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

# Import the models if they exist, otherwise create mock functions
try:
    from posts.models import Post, Like, Comment
    MODELS_LOADED = True
except ImportError:
    MODELS_LOADED = False
    # Mock classes for when models can't be loaded
    class MockPost:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        def save(self):
            return self
    
    Post = MockPost

# Simple logging function
def log(message, level="INFO"):
    """Simple logging function that won't crash"""
    try:
        print(f"[{level}] {message}")
    except:
        pass  # Even printing could fail in some environments

# User posts storage - this replaces mock posts with actual user-created content
USER_POSTS = []

# --- USER FUNCTIONS --- #

@login_required
def current_user(request):
    """
    Returns information about the currently logged-in user
    Used by the frontend to personalize the UI
    """
    user = request.user
    return JsonResponse({
        "id": user.id,
        "username": user.username,
    })

# --- POST FUNCTIONS --- #

@csrf_exempt
@login_required
def create_post(request):
    """Create a new post with support for image uploads"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        log("Create post received")
        
        # Get post data from request
        content = request.POST.get('content', '')
        post_type = request.POST.get('post_type', 'text')
        image = request.FILES.get('image')
        
        # Log request data for debugging
        log(f"Post data - Content: {content}, Type: {post_type}, Has image: {image is not None}")
        
        # Always use USER_POSTS mode for now since we're having DB issues
        image_url = None
        if image and post_type == 'image':
            try:
                # Ensure the media directory exists
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'post_images'), exist_ok=True)
                
                # Generate unique filename
                image_extension = image.name.split('.')[-1] if '.' in image.name else 'jpg'
                unique_filename = f"{uuid.uuid4()}.{image_extension}"
                filename = f"post_images/{unique_filename}"
                
                # Full path for the file
                full_path = os.path.join(settings.MEDIA_ROOT, filename)
                
                # Save the file directly
                with open(full_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)
                
                # Set the URL for frontend access - make sure it starts with /media/
                image_url = f"{settings.MEDIA_URL}{filename}"
                if not image_url.startswith('/'):
                    image_url = f"/{image_url}"
                log(f"Saved image to {full_path}, URL: {image_url}")
            except Exception as e:
                log(f"Error saving image: {e}", "ERROR")
                # In case of error, use a placeholder
                image_url = "https://via.placeholder.com/300x200?text=Image+Not+Available"
        
        # Create a timestamp in ISO format
        timestamp = timezone.now().isoformat()
        
        new_post_id = uuid.uuid4().hex[:8]
        new_post = {
            "id": new_post_id,
            "post_type": post_type,
            "title": content[:20] + "..." if content and len(content) > 20 else content,
            "content": content or "Empty post",
            "author": request.user.username,
            "created_at": timestamp,
            "like_count": 0,
            "comment_count": 0,
            "user_has_liked": False,
            "comments": []
        }
        
        if image_url:
            new_post["image_url"] = image_url
        
        USER_POSTS.insert(0, new_post)
        
        return JsonResponse({
            "success": True,
            "message": "Post created successfully",
            "post": {
                "id": new_post_id,
                "content": content or "Empty post",
                "author": request.user.username,
                "post_type": post_type,
                "image_url": image_url,
                "created_at": timestamp
            }
        })
    except Exception as e:
        log(f"Error in create_post: {e}", "ERROR")
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@login_required
def get_posts(request):
    """Get all posts for the newsfeed"""
    try:
        # Check if we have any user posts, if not, create a starter post
        if not USER_POSTS:
            USER_POSTS.append({
                "id": uuid.uuid4().hex[:8],
                "post_type": "text",
                "title": "Welcome to Connectly",
                "content": "Create your first post by typing something above and clicking Post!",
                "author": request.user.username,
                "created_at": timezone.now().isoformat(),
                "like_count": 0,
                "comment_count": 0,
                "user_has_liked": False,
                "comments": []
            })
        
        # Return user posts
        log(f"Returning {len(USER_POSTS)} user posts")
        return JsonResponse({"posts": USER_POSTS})
    except Exception as e:
        log(f"Error in get_posts: {e}", "ERROR")
        return JsonResponse({"posts": []})

@csrf_exempt
@login_required
def like_post(request, post_id):
    """Like or unlike a post"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        # Find the post and toggle like
        for post in USER_POSTS:
            if str(post["id"]) == str(post_id):
                post["user_has_liked"] = not post["user_has_liked"]
                if post["user_has_liked"]:
                    post["like_count"] += 1
                else:
                    post["like_count"] = max(0, post["like_count"] - 1)
                
                return JsonResponse({
                    "message": "Like toggled successfully",
                    "liked": post["user_has_liked"]
                })
        
        return JsonResponse({"error": "Post not found"}, status=404)
    except Exception as e:
        log(f"Error in like_post: {e}", "ERROR")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@login_required
def comment_post(request, post_id):
    """Add a comment to a post"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        # Parse the comment content
        content = ""
        if request.body:
            try:
                data = json.loads(request.body)
                content = data.get('content', '')
            except:
                content = request.POST.get('content', '')
        
        if not content.strip():
            return JsonResponse({"error": "Comment cannot be empty"}, status=400)
        
        # Find the post and add a comment
        for post in USER_POSTS:
            if str(post["id"]) == str(post_id):
                comment_id = uuid.uuid4().hex[:8]
                timestamp = timezone.now().isoformat()
                
                # Initialize comments list if it doesn't exist
                if "comments" not in post:
                    post["comments"] = []
                
                # Add the comment
                post["comments"].append({
                    "id": comment_id,
                    "user__username": request.user.username,
                    "content": content,
                    "created_at": timestamp
                })
                
                # Update comment count
                post["comment_count"] = len(post["comments"])
                
                return JsonResponse({
                    "message": "Comment added successfully",
                    "id": comment_id,
                    "content": content,
                    "username": request.user.username,
                    "created_at": timestamp
                })
        
        return JsonResponse({"error": "Post not found"}, status=404)
    except Exception as e:
        log(f"Error in comment_post: {e}", "ERROR")
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def get_comments(request, post_id):
    """Get all comments for a post"""
    try:
        # Find the post and return its comments
        for post in USER_POSTS:
            if str(post["id"]) == str(post_id):
                # Return comments if they exist, otherwise return empty list
                comments = post.get("comments", [])
                return JsonResponse({"comments": comments})
        
        # If post not found, return empty comments
        return JsonResponse({"comments": []})
    except Exception as e:
        log(f"Error in get_comments: {e}", "ERROR")
        return JsonResponse({"comments": []})

@csrf_exempt
@login_required
def delete_post(request, post_id):
    """Delete a post"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        # Find and remove the post
        for i, post in enumerate(USER_POSTS):
            if str(post["id"]) == str(post_id):
                # Check if the user is the author
                if post["author"] != request.user.username:
                    return JsonResponse({"error": "Not authorized"}, status=403)
                
                # Delete the image file if it exists
                if "image_url" in post and post["image_url"] and not post["image_url"].startswith("http"):
                    try:
                        # Extract the relative path from the URL
                        image_path = post["image_url"].replace(settings.MEDIA_URL, '')
                        if image_path.startswith('/'):
                            image_path = image_path[1:]
                        
                        full_path = os.path.join(settings.MEDIA_ROOT, image_path)
                        
                        if os.path.exists(full_path):
                            os.remove(full_path)
                            log(f"Deleted image file: {full_path}")
                    except Exception as e:
                        log(f"Error deleting image file: {e}", "ERROR")
                
                del USER_POSTS[i]
                return JsonResponse({"message": "Post deleted successfully"})
        
        return JsonResponse({"error": "Post not found"}, status=404)
    except Exception as e:
        log(f"Error in delete_post: {e}", "ERROR")
        return JsonResponse({"error": str(e)}, status=500)