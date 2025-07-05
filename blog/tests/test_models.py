"""
Tests for blog models.
"""
import pytest
import time
from django.test import TestCase
from blog.models import BlogPost, Comment
import uuid


@pytest.mark.django_db
class TestBlogPostModel:
    """Tests for BlogPost model."""
    
    def test_create_blog_post(self):
        """Test creating a blog post."""
        post = BlogPost.objects.create(
            title="Test Post",
            content="This is a test post content."
        )
        
        assert post.title == "Test Post"
        assert post.content == "This is a test post content."
        assert post.id is not None
        assert post.created_at is not None
        assert post.updated_at is not None
    
    def test_blog_post_str_representation(self):
        """Test string representation of blog post."""
        post = BlogPost.objects.create(
            title="Test Post",
            content="This is a test post content."
        )
        
        assert str(post) == "Test Post"
    
    def test_blog_post_uuid_primary_key(self):
        """Test that blog post uses UUID as primary key."""
        post = BlogPost.objects.create(
            title="Test Post",
            content="This is a test post content."
        )
        
        assert isinstance(post.id, uuid.UUID)
    
    def test_blog_post_timestamps(self):
        """Test that timestamps are automatically set."""
        post = BlogPost.objects.create(
            title="Test Post",
            content="This is a test post content."
        )
        
        assert post.created_at is not None
        assert post.updated_at is not None
        # Permite diferença de até 1 segundo
        diff = abs((post.created_at - post.updated_at).total_seconds())
        assert diff < 1, f"created_at e updated_at diferem por {diff} segundos"
    
    def test_blog_post_updated_at_changes(self):
        """Test that updated_at changes when post is modified."""
        post = BlogPost.objects.create(
            title="Test Post",
            content="This is a test post content."
        )
        
        original_updated_at = post.updated_at
        
        # Add a small delay to ensure timestamp difference
        time.sleep(0.001)
        
        post.title = "Updated Test Post"
        post.save()
        
        assert post.updated_at > original_updated_at


@pytest.mark.django_db
class TestCommentModel:
    """Tests for Comment model."""
    
    def test_create_comment(self, sample_post):
        """Test creating a comment."""
        comment = Comment.objects.create(
            post=sample_post,
            author_name="John Doe",
            content="This is a test comment."
        )
        
        assert comment.post == sample_post
        assert comment.author_name == "John Doe"
        assert comment.content == "This is a test comment."
        assert comment.id is not None
        assert comment.created_at is not None
        assert comment.updated_at is not None
    
    def test_comment_str_representation(self, sample_post):
        """Test string representation of comment."""
        comment = Comment.objects.create(
            post=sample_post,
            author_name="John Doe",
            content="This is a test comment."
        )
        
        expected_str = f"Comment by John Doe on {sample_post.title}"
        assert str(comment) == expected_str
    
    def test_comment_uuid_primary_key(self, sample_post):
        """Test that comment uses UUID as primary key."""
        comment = Comment.objects.create(
            post=sample_post,
            author_name="John Doe",
            content="This is a test comment."
        )
        
        assert isinstance(comment.id, uuid.UUID)
    
    def test_comment_timestamps(self, sample_post):
        """Test that timestamps are automatically set."""
        comment = Comment.objects.create(
            post=sample_post,
            author_name="John Doe",
            content="This is a test comment."
        )
        
        assert comment.created_at is not None
        assert comment.updated_at is not None
        assert comment.created_at == comment.updated_at  # Initially they should be the same
    
    def test_comment_updated_at_changes(self, sample_post):
        """Test that updated_at changes when comment is modified."""
        comment = Comment.objects.create(
            post=sample_post,
            author_name="John Doe",
            content="This is a test comment."
        )
        
        original_updated_at = comment.updated_at
        
        # Add a small delay to ensure timestamp difference
        time.sleep(0.001)
        
        comment.content = "Updated test comment."
        comment.save()
        
        assert comment.updated_at > original_updated_at


@pytest.mark.django_db
class TestModelRelationships:
    """Tests for model relationships."""
    
    def test_post_comments_relationship(self, sample_post):
        """Test that post can have multiple comments."""
        comment1 = Comment.objects.create(
            post=sample_post,
            author_name="John Doe",
            content="First comment."
        )
        comment2 = Comment.objects.create(
            post=sample_post,
            author_name="Jane Smith",
            content="Second comment."
        )
        
        assert sample_post.comments.count() == 2
        assert comment1 in sample_post.comments.all()
        assert comment2 in sample_post.comments.all()
    
    def test_comment_belongs_to_post(self, sample_post):
        """Test that comment belongs to a post."""
        comment = Comment.objects.create(
            post=sample_post,
            author_name="John Doe",
            content="Test comment."
        )
        
        assert comment.post == sample_post
        assert comment.post.title == "Test Post"
    
    def test_cascade_delete(self, sample_post):
        """Test that comments are deleted when post is deleted."""
        Comment.objects.create(
            post=sample_post,
            author_name="John Doe",
            content="Test comment."
        )
        
        assert Comment.objects.count() == 1
        sample_post.delete()
        assert Comment.objects.count() == 0 