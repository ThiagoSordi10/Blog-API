"""
Tests for blog serializers.
"""
import pytest
from blog.serializers import (
    BlogPostSerializer,
    BlogPostDetailSerializer,
    BlogPostListSerializer,
    CommentSerializer
)
from blog.models import BlogPost, Comment


class TestBlogPostSerializer:
    """Tests for BlogPostSerializer."""
    
    def test_blog_post_serializer_valid_data(self):
        """Test BlogPostSerializer with valid data."""
        data = {
            'title': 'Test Post',
            'content': 'This is a test post content.'
        }
        serializer = BlogPostSerializer(data=data)
        
        assert serializer.is_valid()
        assert serializer.validated_data['title'] == 'Test Post'
        assert serializer.validated_data['content'] == 'This is a test post content.'
    
    def test_blog_post_serializer_blank_title(self):
        """Test BlogPostSerializer with blank title."""
        data = {
            'title': '',
            'content': 'This is a test post content.'
        }
        serializer = BlogPostSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'title' in serializer.errors
    
    def test_blog_post_serializer_whitespace_title(self):
        """Test BlogPostSerializer with whitespace-only title."""
        data = {
            'title': '   ',
            'content': 'This is a test post content.'
        }
        serializer = BlogPostSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'title' in serializer.errors
    
    def test_blog_post_serializer_missing_title(self):
        """Test BlogPostSerializer without title."""
        data = {
            'content': 'This is a test post content.'
        }
        serializer = BlogPostSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'title' in serializer.errors
    
    def test_blog_post_serializer_missing_content(self):
        """Test BlogPostSerializer without content."""
        data = {
            'title': 'Test Post'
        }
        serializer = BlogPostSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'content' in serializer.errors
    
    def test_blog_post_serializer_strips_whitespace(self):
        """Test that BlogPostSerializer strips whitespace from title."""
        data = {
            'title': '  Test Post  ',
            'content': 'This is a test post content.'
        }
        serializer = BlogPostSerializer(data=data)
        
        assert serializer.is_valid()
        assert serializer.validated_data['title'] == 'Test Post'


class TestCommentSerializer:
    """Tests for CommentSerializer."""
    
    def test_comment_serializer_valid_data(self):
        """Test CommentSerializer with valid data."""
        data = {
            'author_name': 'John Doe',
            'content': 'This is a test comment with more than 5 characters.'
        }
        serializer = CommentSerializer(data=data)
        
        assert serializer.is_valid()
        assert serializer.validated_data['author_name'] == 'John Doe'
        assert serializer.validated_data['content'] == 'This is a test comment with more than 5 characters.'
    
    def test_comment_serializer_short_content(self):
        """Test CommentSerializer with content shorter than 5 characters."""
        data = {
            'author_name': 'John Doe',
            'content': 'Hi'
        }
        serializer = CommentSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'content' in serializer.errors
    
    def test_comment_serializer_whitespace_content(self):
        """Test CommentSerializer with whitespace-only content."""
        data = {
            'author_name': 'John Doe',
            'content': '   '
        }
        serializer = CommentSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'content' in serializer.errors
    
    def test_comment_serializer_missing_author_name(self):
        """Test CommentSerializer without author name."""
        data = {
            'content': 'This is a test comment.'
        }
        serializer = CommentSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'author_name' in serializer.errors
    
    def test_comment_serializer_missing_content(self):
        """Test CommentSerializer without content."""
        data = {
            'author_name': 'John Doe'
        }
        serializer = CommentSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'content' in serializer.errors
    
    def test_comment_serializer_exact_minimum_length(self):
        """Test CommentSerializer with exactly 5 characters."""
        data = {
            'author_name': 'John Doe',
            'content': '12345'
        }
        serializer = CommentSerializer(data=data)
        
        assert serializer.is_valid()
        assert serializer.validated_data['content'] == '12345'
    
    def test_comment_serializer_strips_whitespace(self):
        """Test that CommentSerializer strips whitespace from content."""
        data = {
            'author_name': 'John Doe',
            'content': '  This is a test comment.  '
        }
        serializer = CommentSerializer(data=data)
        
        assert serializer.is_valid()
        assert serializer.validated_data['content'] == 'This is a test comment.'


@pytest.mark.django_db
class TestBlogPostDetailSerializer:
    """Tests for BlogPostDetailSerializer."""
    
    def test_blog_post_detail_serializer_with_comments(self, sample_post_with_comments):
        """Test BlogPostDetailSerializer with comments."""
        serializer = BlogPostDetailSerializer(sample_post_with_comments)
        data = serializer.data
        
        assert data['id'] == str(sample_post_with_comments.id)
        assert data['title'] == sample_post_with_comments.title
        assert data['content'] == sample_post_with_comments.content
        assert 'comments' in data
        assert len(data['comments']) == 2
        
        # Check comment structure
        for comment in data['comments']:
            assert 'id' in comment
            assert 'author_name' in comment
            assert 'content' in comment
            assert 'created_at' in comment
    
    def test_blog_post_detail_serializer_without_comments(self, sample_post):
        """Test BlogPostDetailSerializer without comments."""
        serializer = BlogPostDetailSerializer(sample_post)
        data = serializer.data
        
        assert data['id'] == str(sample_post.id)
        assert data['title'] == sample_post.title
        assert data['content'] == sample_post.content
        assert 'comments' in data
        assert data['comments'] == []


@pytest.mark.django_db
class TestBlogPostListSerializer:
    """Tests for BlogPostListSerializer."""
    
    def test_blog_post_list_serializer_with_comments(self, sample_post_with_comments):
        """Test BlogPostListSerializer with comments."""
        serializer = BlogPostListSerializer(sample_post_with_comments)
        data = serializer.data
        
        assert data['id'] == str(sample_post_with_comments.id)
        assert data['title'] == sample_post_with_comments.title
        assert 'comment_count' in data
        assert data['comment_count'] == 2
        assert 'content' not in data  # Should not include content in list
    
    def test_blog_post_list_serializer_without_comments(self, sample_post):
        """Test BlogPostListSerializer without comments."""
        serializer = BlogPostListSerializer(sample_post)
        data = serializer.data
        
        assert data['id'] == str(sample_post.id)
        assert data['title'] == sample_post.title
        assert 'comment_count' in data
        assert data['comment_count'] == 0
        assert 'content' not in data  # Should not include content in list 