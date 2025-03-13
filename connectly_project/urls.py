from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from posts.views import (
    homepage, 
    create_user, 
    login_user,
    login_page,  # Make sure this view exists
    test_endpoint,  # Add the test endpoint
    test_json  # Add the JSON test endpoint
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    # Test endpoints for debugging
    path('test/', test_endpoint, name='test_endpoint'),
    path('test_json/', test_json, name='test_json'),
    
    # Main routes
    path('', login_page, name='login'),
    path('login/', login_page, name='login'),
    path('newsfeed/', homepage, name='homepage'),
    path('admin/', admin.site.urls),
    
    # Authentication routes
    path('login_user/', login_user, name="login_user"),
    path('create_user/', create_user, name="create_user"),
    
    # REST framework and JWT
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # App-specific routes
    path('posts/', include('posts.urls')),
    
    # Social authentication
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Add this at the bottom of the file to serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)