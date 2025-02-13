import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from factories.post_factory import PostFactory  # Import the PostFactory
from .models import Post
from .permissions import IsPostAuthor  # Ensure this import is added
from singletons.logger_singleton import LoggerSingleton  # Import the Logger
from rest_framework import status


# Get all users
def get_users(request):
    logger = LoggerSingleton().get_logger()  # Initialize logger
    try:
        users = list(User.objects.values('id', 'username', 'email', 'date_joined'))
        logger.info("Successfully retrieved users.")
        return JsonResponse(users, safe=False)
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_user(request):
    logger = LoggerSingleton().get_logger()  # Initialize logger
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Create the user
            user = User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
            
            # Check if the "admin" group exists, otherwise create it
            admin_group, created = Group.objects.get_or_create(name="admin")
            user.groups.add(admin_group)  # Add the user to the "admin" group
            
            logger.info(f"User created successfully with ID: {user.id}")
            return JsonResponse({'id': user.id, 'message': 'User created successfully'}, status=201)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return JsonResponse({'error': str(e)}, status=400)

# Verify login credentials
@csrf_exempt
def login_user(request):
    logger = LoggerSingleton().get_logger()  # Initialize logger
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = authenticate(username=data['username'], password=data['password'])
            if user is not None:
                logger.info(f"User {data['username']} logged in successfully.")
                return JsonResponse({'message': 'Login successful'}, status=200)
            else:
                logger.warning(f"Invalid login attempt for user {data['username']}.")
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            logger.error(f"Error logging in: {e}")
            return JsonResponse({'error': str(e)}, status=400)

# Create a new post using the PostFactory
class CreatePostView(APIView):
    def post(self, request):
        logger = LoggerSingleton().get_logger()  # Initialize logger
        data = request.data

        # Validate 'metadata' and 'file_size' for image posts
        if 'metadata' not in data or 'file_size' not in data['metadata']:
            logger.error("Missing 'file_size' in metadata for image post.")
            return Response({'error': "Image posts require 'file_size' in metadata"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Using the PostFactory to create a new post
            post = PostFactory.create_post(
                post_type=data['post_type'],
                title=data['title'],
                content=data.get('content', ''),
                metadata=data.get('metadata', {}),
                author=None  # No author required
            )

            logger.info(f"Post created successfully with ID: {post.id}")
            return Response(
                {'message': 'Post created successfully!', 'post_id': post.id},
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            logger.error(f"Error creating post: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Require Authentication for All Endpoints
class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger = LoggerSingleton().get_logger()  # Initialize logger
        logger.info(f"Authenticated access for {request.user.username}.")
        return Response({"message": "Authenticated!"})

# Serializer to exclude sensitive fields
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']  # Exclude sensitive fields like password

# Update a user's email
@csrf_exempt
def update_user(request, id):
    logger = LoggerSingleton().get_logger()  # Initialize logger
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user = User.objects.filter(id=id).first()
            if not user:
                logger.warning(f"User with ID {id} not found.")
                return JsonResponse({'error': 'User not found'}, status=404)
            user.email = data.get('email', user.email)
            user.save()
            logger.info(f"User with ID {id} updated successfully.")
            return JsonResponse({'message': 'User updated successfully'}, status=200)
        except Exception as e:
            logger.error(f"Error updating user with ID {id}: {e}")
            return JsonResponse({'error': str(e)}, status=400)

# Delete a user
@csrf_exempt
def delete_user(request, id):
    logger = LoggerSingleton().get_logger()  # Initialize logger
    if request.method == 'DELETE':
        try:
            user = User.objects.filter(id=id).first()
            if not user:
                logger.warning(f"User with ID {id} not found.")
                return JsonResponse({'error': 'User not found'}, status=404)
            user.delete()
            logger.info(f"User with ID {id} deleted successfully.")
            return JsonResponse({'message': 'User deleted successfully'}, status=200)
        except Exception as e:
            logger.error(f"Error deleting user with ID {id}: {e}")
            return JsonResponse({'error': str(e)}, status=400)

# Restrict Views to Specific Roles
class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure user is authenticated
    permission_classes += [IsPostAuthor]  # Add custom permission for post authors

    def get(self, request, pk):
        logger = LoggerSingleton().get_logger()  # Initialize logger
        post = Post.objects.get(pk=pk)
        self.check_object_permissions(request, post)  # Check permissions for the object
        logger.info(f"Post content retrieved with ID {pk}.")
        return Response({"content": post.content})  # Send the content of the post
