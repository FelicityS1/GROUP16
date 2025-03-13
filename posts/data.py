import json
import logging
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db.models import UUIDField
from .models import Post, Like, Comment
import uuid

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def get_user_data(request):
    """Return current user data for the frontend"""
    return JsonResponse({
        "id": str(request.user.id),
        "username": request.user.username,
        "email": request.user.email
    })

@csrf_exempt
@login_required
def handle_like(request, post_id):
    """Handles liking/unliking a post"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        uuid_post_id = uuid.UUID(post_id, version=4)
        post = get_object_or_404(Post, id=uuid_post_id)
    except ValueError:
        return JsonResponse({"error": "Invalid post ID format"}, status=400)
    
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    return JsonResponse({
        "success": True,
        "liked": liked,
        "like_count": Like.objects.filter(post=post).count()
    })

@csrf_exempt
@login_required
def handle_comment(request, post_id):
    """Handles adding a comment to a post"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        uuid_post_id = uuid.UUID(post_id, version=4)
        post = get_object_or_404(Post, id=uuid_post_id)
    except ValueError:
        return JsonResponse({"error": "Invalid post ID format"}, status=400)
    
    try:
        data = json.loads(request.body)
        content = data.get("content", "").strip()
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    
    if not content:
        return JsonResponse({"error": "Comment cannot be empty"}, status=400)
    
    comment = Comment.objects.create(user=request.user, post=post, content=content)
    
    return JsonResponse({
        "success": True,
        "comment": {
            "id": str(comment.id),
            "content": comment.content,
            "user": request.user.username,
            "created_at": comment.created_at.isoformat()
        },
        "comment_count": Comment.objects.filter(post=post).count()
    })

@csrf_exempt
@login_required
def get_post_comments(request, post_id):
    """Retrieve all comments for a post"""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        uuid_post_id = uuid.UUID(post_id, version=4)
        post = get_object_or_404(Post, id=uuid_post_id)
    except ValueError:
        return JsonResponse({"error": "Invalid post ID format"}, status=400)
    
    comments = Comment.objects.filter(post=post).order_by("created_at").values(
        "id", "content", "created_at", "user__username"
    )
    
    return JsonResponse({"success": True, "comments": list(comments)})

@csrf_exempt
@login_required
def handle_delete_post(request, post_id):
    """Delete a post"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        uuid_post_id = uuid.UUID(post_id, version=4)
        post = get_object_or_404(Post, id=uuid_post_id)
    except ValueError:
        return JsonResponse({"error": "Invalid post ID format"}, status=400)
    
    if post.author != request.user:
        return JsonResponse({"error": "You are not authorized to delete this post"}, status=403)
    
    post.delete()
    return JsonResponse({"success": True, "message": "Post deleted successfully"})
