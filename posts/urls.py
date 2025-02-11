from django.urls import path
from . import views

urlpatterns = [
    # Existing paths
    path('users/', views.get_users, name='get_users'),
    path('create_user/', views.create_user, name='create_user'),
    path('login_user/', views.login_user, name='login_user'),
    path('update_user/<int:id>/', views.update_user, name='update_user'),
    path('delete_user/<int:id>/', views.delete_user, name='delete_user'),
    path('protected/', views.ProtectedView.as_view(), name='protected'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
]
