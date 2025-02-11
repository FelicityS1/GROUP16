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
from .models import Post
from .permissions import IsPostAuthor  # Ensure this import is added


# Get all users
def get_users(request):
    try:
        # Replaced 'created_at' with 'date_joined'
        users = list(User.objects.values('id', 'username', 'email', 'date_joined'))
        return JsonResponse(users, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Create a new user with password encryption
@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Use Django's create_user method to hash the password
            user = User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
            
            # Assign user to a role/group (RBAC)
            admin_group = Group.objects.create(name="admin")  # Create an "admin" group
            user.groups.add(admin_group)  # Add the user to the "admin" group
            
            return JsonResponse({'id': user.id, 'message': 'User created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# Verify login credentials
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Use Django's authenticate method to validate credentials
            user = authenticate(username=data['username'], password=data['password'])
            if user is not None:
                return JsonResponse({'message': 'Login successful'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# Require Authentication for All Endpoints
class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Authenticated!"})

# Serializer to exclude sensitive fields
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']  # Exclude sensitive fields like password

# Update a user's email
@csrf_exempt
def update_user(request, id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user = User.objects.filter(id=id).first()
            if not user:
                return JsonResponse({'error': 'User not found'}, status=404)
            user.email = data.get('email', user.email)
            user.save()
            return JsonResponse({'message': 'User updated successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# Delete a user
@csrf_exempt
def delete_user(request, id):
    if request.method == 'DELETE':
        try:
            user = User.objects.filter(id=id).first()
            if not user:
                return JsonResponse({'error': 'User not found'}, status=404)
            user.delete()
            return JsonResponse({'message': 'User deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# Restrict Views to Specific Roles
class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure user is authenticated
    permission_classes += [IsPostAuthor]  # Add custom permission for post authors

    def get(self, request, pk):
        post = Post.objects.get(pk=pk)
        self.check_object_permissions(request, post)  # Check permissions for the object
        return Response({"content": post.content})  # Send the content of the post
