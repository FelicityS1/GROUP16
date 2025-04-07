# role_required.py

from functools import wraps
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

def role_required(allowed_roles):
    """
    Decorator to check if the user has one of the allowed roles.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Authentication required"}, status=401)
            
            # Get user role - from user profile or groups
            user_role = None
            
            # First try to get role from profile
            if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'role'):
                user_role = request.user.profile.role
            
            # If no profile role, check if user is in admin group
            elif request.user.groups.filter(name='admin').exists():
                user_role = 'admin'
            else:
                user_role = 'user'  # Default role if no other role found
            
            # Check if user has one of the allowed roles
            if user_role not in allowed_roles:
                return JsonResponse({
                    "error": "You don't have permission to perform this action.",
                    "required_roles": allowed_roles,
                    "your_role": user_role
                }, status=403)
                
            # Add role to request for convenient access in views
            request.user_role = user_role
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """
    Decorator to require that the user is an admin.
    """
    return role_required(['admin'])(view_func)


def moderator_or_admin_required(view_func):
    """
    Decorator to require that the user is either a moderator or an admin.
    """
    return role_required(['admin', 'moderator'])(view_func)


def is_post_owner_or_has_role(allowed_roles):
    """
    Decorator to check if the user is the owner of the post or has a specific role.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, post_id, *args, **kwargs):
            from .models import Post  # Import here to avoid circular imports
            
            # Get the post
            try:
                post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                return JsonResponse({"error": "Post not found"}, status=404)
            
            # Get user role
            user_role = None
            if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'role'):
                user_role = request.user.profile.role
            elif request.user.groups.filter(name='admin').exists():
                user_role = 'admin'
            else:
                user_role = 'user'
            
            # Check if user is the post author or has required role
            if post.author != request.user and user_role not in allowed_roles:
                return JsonResponse({
                    "error": "You don't have permission to perform this action on this post.",
                    "required_roles": allowed_roles,
                    "your_role": user_role
                }, status=403)
                
            return view_func(request, post_id, *args, **kwargs)
        return _wrapped_view
    return decorator