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


class BlogPostDetailView(generics.RetrieveAPIView):
    """
    GET /api/posts/{id} - Retrieve a specific post with comments
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostDetailSerializer
    lookup_field = 'id'


class CommentCreateView(generics.CreateAPIView):
    """
    POST /api/posts/{id}/comments - Add a new comment to the post
    """
    serializer_class = CommentSerializer
    
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(BlogPost, id=post_id)
        serializer.save(post=post)
