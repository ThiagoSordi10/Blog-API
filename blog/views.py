from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import BlogPost, Comment
from .serializers import (
    BlogPostSerializer,
    BlogPostDetailSerializer,
    BlogPostListSerializer,
    CommentSerializer
)
from .cache_helpers import BlogCacheHelper


class BlogPostListCreateView(generics.ListCreateAPIView):
    """
    GET /api/posts - List all posts with comment count
    POST /api/posts - Create a new post
    """
    queryset = BlogPost.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BlogPostListSerializer
        return BlogPostSerializer
    
    def get(self, request, *args, **kwargs):
        """Override get to implement caching for posts list."""
        cached_data = BlogCacheHelper.get_posts_list()
        if cached_data is not None:
            return Response(cached_data)
        
        response = super().get(request, *args, **kwargs)
        
        BlogCacheHelper.set_posts_list(response.data)
        
        return response
    
    def perform_create(self, serializer):
        """Override perform_create to invalidate cache on new post."""
        post = serializer.save()
        BlogCacheHelper.invalidate_posts_list()
        return post


class BlogPostDetailView(generics.RetrieveAPIView):
    """
    GET /api/posts/{id} - Retrieve a specific post with comments
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostDetailSerializer
    lookup_field = 'id'
    
    def get(self, request, *args, **kwargs):
        """Override get to implement caching for post detail."""
        post_id = self.kwargs.get('id')
        
        cached_data = BlogCacheHelper.get_post_detail(post_id)
        if cached_data is not None:
            return Response(cached_data)
        
        response = super().get(request, *args, **kwargs)
        
        BlogCacheHelper.set_post_detail(post_id, response.data)
        
        return response


class CommentCreateView(generics.CreateAPIView):
    """
    POST /api/posts/{id}/comments - Add a new comment to the post
    """
    serializer_class = CommentSerializer
    
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(BlogPost, id=post_id)
        comment = serializer.save(post=post)
        
        BlogCacheHelper.invalidate_all_post_cache(post_id)
        
        return comment
