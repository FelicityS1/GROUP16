import json
import os
import uuid
from rest_framework.views import APIView
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, status
from factories.post_factory import PostFactory
from .models import Post, Like, Comment
from django.conf.urls.static import static
from django.conf import settings
from .permissions import IsPostAuthor
from singletons.logger_singleton import LoggerSingleton
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from allauth.socialaccount.models import SocialApp
from django.middleware.csrf import get_token


@ensure_csrf_cookie
def login_page(request):
    """
    Display login page and handle login form submissions.
    """
    # If this is a POST request, process the form data
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Basic validation
        if not username or not password:
            return render(request, 'index.html', {'error': 'Username and password are required'})
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Login successful
            login(request, user)
            return redirect('/newsfeed/')
        else:
            # Invalid credentials
            return render(request, 'index.html', {'error': 'Invalid username or password'})
    
    # If GET or any other method, just display the login page
    return render(request, 'index.html', {
        'static_url': settings.STATIC_URL
    })

def homepage(request):
    """
    Display the homepage/newsfeed after successful login.
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect('/login/')
    
    return render(request, 'newsfeed.html')

@login_required
def current_user(request):
    """
    Returns information about the currently logged in user
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    return JsonResponse({
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email
    })

# Get all users
def get_users(request):
    logger = LoggerSingleton().get_logger()
    try:
        User = get_user_model()
        users = list(User.objects.values("id", "username", "email", "date_joined"))
        logger.info("Successfully retrieved users.")
        return JsonResponse(users, safe=False)
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def create_user(request):
    logger = LoggerSingleton().get_logger()
    if request.method == "POST":
        try:
            # Handle both JSON API requests and form submissions
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
                
            User = get_user_model()
            user = User.objects.create_user(
                username=data["username"], 
                email=data["email"], 
                password=data["password"]
            )
            admin_group, created = Group.objects.get_or_create(name="admin")
            user.groups.add(admin_group)
            logger.info(f"User created successfully with ID: {user.id}")
            
            # For form submissions, log the user in and redirect
            if request.content_type != 'application/json':
                login(request, user)
                return redirect('homepage')
                
            return JsonResponse({"id": user.id, "message": "User created successfully"}, status=201)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return JsonResponse({"error": str(e)}, status=400)
    
    # For GET requests to this endpoint, show signup form
    return render(request, 'signup.html')


@csrf_exempt
def login_user(request):
    """
    A simplified login view that will definitely work.
    """
    print(f"Received {request.method} request at login_user/")
    
    if request.method == "GET":
        return HttpResponse("Login endpoint is working!")
    
    if request.method == "POST":
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                    print(f"Received JSON data: {data}")
                except json.JSONDecodeError:
                    print("Invalid JSON received")
                    return JsonResponse({"success": False, "error": "Invalid JSON format"})
            else:
                data = request.POST
                print(f"Received form data: {data}")
                
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                print("Missing username or password")
                return JsonResponse({"success": False, "error": "Username and password are required"})

            print(f"Authenticating user: {username}")
            user = authenticate(username=username, password=password)

            if user is not None:
                print(f"User {username} authenticated successfully")
                login(request, user)
                return JsonResponse({"success": True, "redirect": "/newsfeed/"})
            else:
                print(f"Authentication failed for {username}")
                return JsonResponse({"success": False, "error": "Invalid username or password"})
                
        except Exception as e:
            print(f"Server error during login: {str(e)}")
            return JsonResponse({"success": False, "error": f"Server error: {str(e)}"})
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

        
def update_user(request, id):
    if request.method == "PUT":
        try:
            User = get_user_model()
            user = get_object_or_404(User, id=id)
            data = json.loads(request.body)

            user.username = data.get("username", user.username)
            user.email = data.get("email", user.email)
            user.save()

            return JsonResponse({"message": "User updated successfully!"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def delete_user(request, id):
    """
    Deletes a user by ID.
    """
    if request.method == "DELETE":
        try:
            User = get_user_model()
            user = get_object_or_404(User, id=id)
            user.delete()
            return JsonResponse({"message": "User deleted successfully!"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def test_endpoint(request):
    """
    A simple test endpoint to verify the Django server is working correctly.
    """
    if request.method == "GET":
        return HttpResponse(
            "<html><body><h1>Test Endpoint Working!</h1>"
            "<p>Your Django server is responding correctly.</p>"
            "<p>Try the <a href='/test_json/'>JSON test endpoint</a> too.</p>"
            "</body></html>"
        )
    elif request.method == "POST":
        return HttpResponse("POST request received successfully!")
    else:
        return HttpResponse("Unsupported method", status=405)

@csrf_exempt
def test_json(request):
    """
    A test endpoint that returns JSON to test if JSON responses work.
    """
    return JsonResponse({
        "success": True,
        "message": "JSON endpoint is working!",
        "method": request.method,
        "content_type": request.content_type
    })

# Add the new delete_post function to views.py

@csrf_exempt
@login_required
def delete_post(request, post_id):
    """
    Delete a post
    """
    logger = LoggerSingleton().get_logger()
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        post = get_object_or_404(Post, id=post_id)
        
        # Check if the user is the author of the post
        if post.author != request.user:
            return JsonResponse({"error": "You don't have permission to delete this post"}, status=403)
        
        # Delete any associated images if they exist
        if post.post_type == 'image' and post.metadata and 'image_path' in post.metadata:
            image_path = post.metadata['image_path']
            # Use default_storage to delete the file
            try:
                default_storage.delete(image_path)
                logger.info(f"Deleted image: {image_path}")
            except Exception as e:
                logger.error(f"Error deleting image: {e}")
        
        # Delete the post
        post.delete()
        logger.info(f"Post {post_id} deleted by user {request.user.username}")
        
        return JsonResponse({"message": "Post deleted successfully"})
        
    except Exception as e:
        logger.error(f"Error deleting post: {e}")
        return JsonResponse({"error": str(e)}, status=400)

# Fix the create_post view function to properly handle image uploads
@csrf_exempt
def create_post(request):
    """
    Creates a new post
    """
    # Fix for logger - avoid any possible circular imports
    import logging
    logger = logging.getLogger(__name__)
    
    if request.method == "POST":
        try:
            # Handle both JSON API requests and form submissions
            if request.content_type and 'application/json' in request.content_type:
                data = json.loads(request.body)
            else:
                data = request.POST
                
            # Get basic post data
            title = data.get("title", "")
            content = data.get("content", "")
            post_type = data.get("post_type", "text")
            
            # Handle image upload if present
            image_file = request.FILES.get('image')
            metadata = {}
            
            if post_type == 'image' and image_file:
                # Generate a unique file path
                file_ext = os.path.splitext(image_file.name)[1]
                unique_filename = f"{uuid.uuid4()}{file_ext}"
                file_path = f"post_images/{unique_filename}"
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'post_images'), exist_ok=True)
                
                # Save the file
                path = default_storage.save(file_path, ContentFile(image_file.read()))
                
                # Store metadata
                metadata = {
                    'file_size': image_file.size,
                    'file_type': image_file.content_type,
                    'image_path': file_path
                }
            else:
                # Use metadata from POST data if provided
                metadata_str = data.get("metadata", "{}")
                try:
                    if isinstance(metadata_str, str):
                        metadata = json.loads(metadata_str)
                    else:
                        metadata = metadata_str
                except json.JSONDecodeError:
                    metadata = {}
            
            # FIX: Get actual User object instead of SimpleLazyObject
            author = None
            if request.user.is_authenticated:
                # Get the actual User model instance instead of the SimpleLazyObject
                User = get_user_model()
                author = User.objects.get(pk=request.user.pk)
            
            # Create the post with proper author object
            post = Post.objects.create(
                title=title,
                content=content,
                post_type=post_type,
                metadata=metadata,
                author=author
            )
            
            logger.info(f"Post created successfully with ID: {post.id}")
            return JsonResponse({
                "message": "Post created successfully!", 
                "post_id": post.id
            }, status=201)
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)


def get_posts(request):
    posts = Post.objects.all().order_by('-created_at')

    post_list = [
        {
            "id": str(post.id),  # Convert UUID to string
            "post_type": post.post_type,
            "title": post.metadata.get("title", "Untitled") if post.metadata else "Untitled",
            "content": post.content,
            "author": post.author.username,
            "created_at": post.created_at.isoformat(),
            "like_count": post.like_count(),
            "comment_count": post.comment_count(),
            "user_has_liked": False,
            "comments": [],
        } 
        for post in posts
    ]

    return JsonResponse({"posts": post_list})


# ️API views for posts
class CreatePostView(APIView):
    """
    API view for creating posts
    """
    def post(self, request):
        try:
            data = request.data
            
            # Basic validation
            if 'content' not in data:
                return Response({"error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)
                
            post_type = data.get('post_type', 'text')
            title = data.get('title', '')
            
            # Create the post
            post = Post.objects.create(
                post_type=post_type,
                title=title,
                content=data.get('content', ''),
                author=request.user if request.user.is_authenticated else None,
                metadata=data.get('metadata', {})
            )
            
            return Response({
                "message": "Post created successfully!", 
                "post_id": post.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ️Add like post function
@csrf_exempt
@login_required
def like_post(request, post_id):
    """
    Like/unlike a post
    """
    logger = LoggerSingleton().get_logger()
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        post = get_object_or_404(Post, id=post_id)
        
        # Check if the user already liked this post
        existing_like = Like.objects.filter(user=request.user, post=post).first()
        
        if existing_like:
            # User already liked the post, so unlike it (toggle behavior)
            existing_like.delete()
            logger.info(f"Post {post_id} unliked by user {request.user.username}")
            return JsonResponse({"message": "Post unliked successfully", "liked": False})
        else:
            # User hasn't liked the post, so like it
            Like.objects.create(user=request.user, post=post)
            logger.info(f"Post {post_id} liked by user {request.user.username}")
            return JsonResponse({"message": "Post liked successfully", "liked": True})
            
    except Exception as e:
        logger.error(f"Error liking post: {e}")
        return JsonResponse({"error": str(e)}, status=400)


# ️Add comment post function
@csrf_exempt
@login_required
def comment_post(request, post_id):
    """
    Add a comment to a post
    """
    logger = LoggerSingleton().get_logger()
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        post = get_object_or_404(Post, id=post_id)
        
        # Get comment content from request body
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
        except json.JSONDecodeError:
            # Handle form data
            content = request.POST.get('content', '').strip()
        
        if not content:
            return JsonResponse({"error": "Comment content cannot be empty"}, status=400)
        
        # Create the comment
        comment = Comment.objects.create(
            user=request.user,
            post=post,
            content=content
        )
        
        logger.info(f"Comment added to post {post_id} by user {request.user.username}")
        
        return JsonResponse({
            "message": "Comment added successfully",
            "id": comment.id,
            "content": comment.content,
            "username": request.user.username,
            "created_at": comment.created_at.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error commenting on post: {e}")
        return JsonResponse({"error": str(e)}, status=400)


# Class-based API views
class LikePostView(APIView):
    """
    API view for liking posts
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, id):
        # Ensure user is authenticated
        if not request.user.is_authenticated:
            return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        # Get the post
        post = get_object_or_404(Post, id=id)

        # Prevent duplicate likes
        if Like.objects.filter(user=request.user, post=post).exists():
            return Response({"message": "You already liked this post"}, status=status.HTTP_400_BAD_REQUEST)

        # Create like instance
        Like.objects.create(user=request.user, post=post)
        return Response({"message": "Post liked successfully!"}, status=status.HTTP_201_CREATED)


class CommentPostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        post = get_object_or_404(Post, id=id)
        data = request.data

        if "content" not in data or not data["content"].strip():
            return Response({"error": "Comment content cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        Comment.objects.create(user=request.user, post=post, content=data["content"])
        return Response({"message": "Comment added successfully!"}, status=status.HTTP_201_CREATED)


class GetCommentsView(APIView):
    def get(self, request, id):
        post = get_object_or_404(Post, id=id)
        comments = post.comments.values("user__username", "content", "created_at")
        return Response({"comments": list(comments)}, status=status.HTTP_200_OK)


class PostDetailView(APIView):
    def get(self, request, id):
        post = get_object_or_404(Post, id=id)
        response_data = {
            "title": post.title,
            "content": post.content,
            "author": post.author.username if post.author else "Anonymous",
            "created_at": post.created_at,
            "like_count": post.like_count(),
            "comment_count": post.comment_count(),
        }
        return Response(response_data, status=status.HTTP_200_OK)