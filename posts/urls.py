from django.urls import path
from . import views
from .views import create_user, login_user, CreatePostView

urlpatterns = [
    # Existing paths
    path('users/', views.get_users, name='get_users'),
    path('create_user/', views.create_user, name='create_user'),
    path('login_user/', views.login_user, name='login_user'),
    path('update_user/<int:id>/', views.update_user, name='update_user'),
    path('delete_user/<int:id>/', views.delete_user, name='delete_user'),
    path('create_post/', CreatePostView.as_view(), name='create_post'),
    path('protected/', views.ProtectedView.as_view(), name='protected'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
]
