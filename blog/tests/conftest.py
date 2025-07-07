"""
Shared fixtures for blog API tests.
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from blog.models import BlogPost, Comment
import uuid


@pytest.fixture
def api_client():
    """API client for testing."""
    return APIClient()


@pytest.fixture
def sample_user():
    """Create a sample user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def sample_post(sample_user):
    """Create a sample blog post."""
    return BlogPost.objects.create(
        title="Test Post",
        content="This is a test post content.",
        author=sample_user
    )


@pytest.fixture
def sample_post_with_comments(sample_post, sample_user):
    """Create a sample post with comments."""
    Comment.objects.create(
        post=sample_post,
        author=sample_user,
        content="This is a test comment."
    )
    Comment.objects.create(
        post=sample_post,
        author=sample_user,
        content="This is another test comment."
    )
    return sample_post


@pytest.fixture
def multiple_posts(sample_user):
    """Create multiple blog posts."""
    posts = []
    for i in range(3):
        post = BlogPost.objects.create(
            title=f"Test Post {i+1}",
            content=f"This is test post content {i+1}.",
            author=sample_user
        )
        posts.append(post)
    return posts


@pytest.fixture
def non_existent_uuid():
    """Non-existent UUID for testing."""
    return str(uuid.uuid4()) 