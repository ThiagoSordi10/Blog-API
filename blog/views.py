from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import BlogPost, Comment
from .serializers import (
    BlogPostSerializer,
    BlogPostDetailSerializer,
    BlogPostListSerializer,
    CommentSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer
)
from .cache_helpers import BlogCacheHelper


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register - Register a new user
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(generics.GenericAPIView):
    """
    POST /api/auth/login - Login user and return token
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })


class UserProfileView(generics.RetrieveAPIView):
    """
    GET /api/auth/profile - Get current user profile
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class BlogPostListCreateView(generics.ListCreateAPIView):
    """
    GET /api/posts - List all posts with comment count
    POST /api/posts - Create a new post (requires authentication)
    """
    queryset = BlogPost.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BlogPostListSerializer
        return BlogPostSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def get(self, request, *args, **kwargs):
        """Override get to implement caching for posts list."""
        cached_data = BlogCacheHelper.get_posts_list()
        if cached_data is not None:
            return Response(cached_data)
        
        response = super().get(request, *args, **kwargs)
        
        BlogCacheHelper.set_posts_list(response.data)
        
        return response
    
    def perform_create(self, serializer):
        """Override perform_create to associate user and invalidate cache on new post."""
        post = serializer.save(author=self.request.user)
        BlogCacheHelper.invalidate_posts_list()
        return post


class BlogPostDetailView(generics.RetrieveAPIView):
    """
    GET /api/posts/{id} - Retrieve a specific post with comments
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostDetailSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]
    
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
    POST /api/posts/{id}/comments - Add a new comment to the post (requires authentication)
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(BlogPost, id=post_id)
        comment = serializer.save(post=post, author=self.request.user)
        
        BlogCacheHelper.invalidate_all_post_cache(post_id)
        
        return comment
