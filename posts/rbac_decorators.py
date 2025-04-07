from functools import wraps
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Post
from django.contrib.auth.decorators import login_required


def role_required(allowed_roles):
    """
    Decorator to check if the user has one of the allowed roles.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check if user has the required role
            if not hasattr(request.user, 'profile') or request.user.profile.role not in allowed_roles:
                return JsonResponse({"error": "You don't have permission to view this page."}, status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """
    Decorator to require that the user is an admin.
    """
    return role_required(['admin'])(view_func)


def is_post_owner_or_has_role(allowed_roles):
    """
    Decorator to check if the user is the owner of the post or has a specific role.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, post_id, *args, **kwargs):
            # Check if the user is the owner of the post or has a required role
            post = get_object_or_404(Post, id=post_id)
            if post.author != request.user and (not hasattr(request.user, 'profile') or request.user.profile.role not in allowed_roles):
                return JsonResponse({"error": "You don't have permission to view or edit this post."}, status=403)
            return view_func(request, post_id, *args, **kwargs)
        return _wrapped_view
    return decorator
