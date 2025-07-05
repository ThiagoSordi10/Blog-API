from django.urls import path
from .views import BlogPostListCreateView, BlogPostDetailView, CommentCreateView

app_name = 'blog'

urlpatterns = [
    # GET /api/posts - List all posts with comment count
    # POST /api/posts - Create a new post
    path('api/posts/', BlogPostListCreateView.as_view(), name='post-list-create'),
    
    # GET /api/posts/{id} - Retrieve a specific post with comments
    path('api/posts/<uuid:id>/', BlogPostDetailView.as_view(), name='post-detail'),
    
    # POST /api/posts/{id}/comments - Add a new comment to the post
    path('api/posts/<uuid:post_id>/comments/', CommentCreateView.as_view(), name='comment-create'),
] 