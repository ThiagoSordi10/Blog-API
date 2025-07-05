"""
Shared fixtures for blog API tests.
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from blog.models import BlogPost, Comment
import uuid


@pytest.fixture
def api_client():
    """API client for testing."""
    return APIClient()


@pytest.fixture
def sample_post():
    """Create a sample blog post."""
    return BlogPost.objects.create(
        title="Test Post",
        content="This is a test post content."
    )


@pytest.fixture
def sample_post_with_comments(sample_post):
    """Create a sample post with comments."""
    Comment.objects.create(
        post=sample_post,
        author_name="John Doe",
        content="This is a test comment."
    )
    Comment.objects.create(
        post=sample_post,
        author_name="Jane Smith",
        content="This is another test comment."
    )
    return sample_post


@pytest.fixture
def multiple_posts():
    """Create multiple blog posts."""
    posts = []
    for i in range(3):
        post = BlogPost.objects.create(
            title=f"Test Post {i+1}",
            content=f"This is test post content {i+1}."
        )
        posts.append(post)
    return posts


@pytest.fixture
def non_existent_uuid():
    """Non-existent UUID for testing."""
    return str(uuid.uuid4()) 