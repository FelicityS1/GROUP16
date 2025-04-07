from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.contrib.auth import get_user_model
import json
from .models import Post, Like, Comment
from .rbac_decorators import role_required, admin_required
from singletons.logger_singleton import LoggerSingleton

logger = LoggerSingleton().get_logger()

@login_required
@role_required(['admin', 'moderator'])
def admin_panel(request):
    """
    Admin panel view - only accessible to admins and moderators
    """
    return render(request, 'admin_panel.html')

@login_required
@role_required(['admin', 'moderator'])
def admin_get_users(request):
    """
    API endpoint to get all users - only accessible to admins and moderators
    """
    try:
        User = get_user_model()
        users = User.objects.all().order_by('-date_joined')
        
        user_list = []
        for user in users:
            role = user.profile.role if hasattr(user, 'profile') else 'user'
            user_list.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": role,
                "date_joined": user.date_joined.isoformat()
            })
        
        return JsonResponse({"users": user_list})
        
    except Exception as e:
        logger.error(f"Error fetching users in admin panel: {e}")
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@login_required
@admin_required
def admin_update_user_role(request, user_id):
    """
    API endpoint to update a user's role - only accessible to admins
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        # Get the target user
        User = get_user_model()
        target_user = get_object_or_404(User, id=user_id)
        
        # Get the new role from the request
        try:
            data = json.loads(request.body)
            new_role = data.get('role', '').strip()
        except json.JSONDecodeError:
            new_role = request.POST.get('role', '').strip()
        
        # Validate the role
        valid_roles = ['admin', 'moderator', 'user', 'guest']
        if new_role not in valid_roles:
            return JsonResponse({"error": f"Invalid role. Must be one of: {', '.join(valid_roles)}"}, status=400)
        
        # Prevent demoting yourself from admin role
        if target_user == request.user and new_role != 'admin':
            return JsonResponse({"error": "You cannot demote yourself from the admin role"}, status=400)
        
        # Update the user's role
        if not hasattr(target_user, 'profile'):
            # Create profile if it doesn't exist
            from .user_profile import UserProfile
            UserProfile.objects.create(user=target_user, role=new_role)
        else:
            profile = target_user.profile
            profile.role = new_role
            profile.save()
        
        logger.info(f"User {target_user.username} role updated to {new_role} by {request.user.username}")
        
        return JsonResponse({"message": f"User role updated to {new_role}"})
        
    except Exception as e:
        logger.error(f"Error updating user role: {e}")
        return JsonResponse({"error": str(e)}, status=400)

@login_required
@role_required(['admin', 'moderator'])
def admin_get_statistics(request):
    """
    API endpoint to get site statistics - only accessible to admins and moderators
    """
    try:
        post_count = Post.objects.count()
        comment_count = Comment.objects.count()
        like_count = Like.objects.count()
        user_count = get_user_model().objects.count()
        
        # Get count by privacy setting
        public_posts = Post.objects.filter(privacy='public').count() if hasattr(Post, 'privacy') else 'N/A'
        private_posts = Post.objects.filter(privacy='private').count() if hasattr(Post, 'privacy') else 'N/A'
        friends_posts = Post.objects.filter(privacy='friends').count() if hasattr(Post, 'privacy') else 'N/A'
        
        return JsonResponse({
            "post_count": post_count,
            "comment_count": comment_count,
            "like_count": like_count,
            "user_count": user_count,
            "public_posts": public_posts,
            "private_posts": private_posts,
            "friends_posts": friends_posts
        })
        
    except Exception as e:
        logger.error(f"Error fetching site statistics: {e}")
        return JsonResponse({"error": str(e)}, status=400)

@login_required
@admin_required
def initialize_roles(request):
    """
    Initialize roles for all users who don't have a role yet
    """
    try:
        from .user_profile import UserProfile
        User = get_user_model()
        
        # Get all users without profiles
        users_without_profiles = []
        for user in User.objects.all():
            if not hasattr(user, 'profile'):
                users_without_profiles.append(user)
        
        # Create profiles with default role
        for user in users_without_profiles:
            UserProfile.objects.create(user=user, role='user')
        
        # Set the requesting user as admin if they aren't already
        if request.user.profile.role != 'admin':
            request.user.profile.role = 'admin'
            request.user.profile.save()
        
        return JsonResponse({
            "message": f"Initialized roles for {len(users_without_profiles)} users",
            "your_role": "admin"
        })
        
    except Exception as e:
        logger.error(f"Error initializing roles: {e}")
        return JsonResponse({"error": str(e)}, status=400)