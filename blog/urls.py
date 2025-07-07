from django.urls import path
from .views import (
    BlogPostListCreateView, 
    BlogPostDetailView, 
    CommentCreateView,
    RegisterView,
    LoginView,
    UserProfileView
)

app_name = 'blog'

urlpatterns = [
    # Authentication endpoints
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/profile/', UserProfileView.as_view(), name='profile'),
    
    # Blog endpoints
    # GET /api/posts - List all posts with comment count
    # POST /api/posts - Create a new post
    path('api/posts/', BlogPostListCreateView.as_view(), name='post-list-create'),
    
    # GET /api/posts/{id} - Retrieve a specific post with comments
    path('api/posts/<uuid:id>/', BlogPostDetailView.as_view(), name='post-detail'),
    
    # POST /api/posts/{id}/comments - Add a new comment to the post
    path('api/posts/<uuid:post_id>/comments/', CommentCreateView.as_view(), name='comment-create'),
] 