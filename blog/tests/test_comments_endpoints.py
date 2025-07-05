"""
Tests for comment endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from blog.models import Comment


@pytest.mark.django_db
class TestCommentCreateEndpoint:
    """Tests for POST /api/posts/{id}/comments endpoint."""
    
    def test_create_comment_success(self, api_client, sample_post):
        """Test creating a new comment successfully."""
        url = reverse('blog:comment-create', kwargs={'post_id': sample_post.id})
        data = {
            'author_name': 'John Doe',
            'content': 'This is a test comment with more than 5 characters.'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['author_name'] == data['author_name']
        assert response.data['content'] == data['content']
        assert 'id' in response.data
        assert 'created_at' in response.data
        
        # Verify comment was created in database
        assert Comment.objects.count() == 1
        comment = Comment.objects.first()
        assert comment.post == sample_post
        assert comment.author_name == data['author_name']
    
    def test_create_comment_short_content(self, api_client, sample_post):
        """Test creating comment with content shorter than 5 characters."""
        url = reverse('blog:comment-create', kwargs={'post_id': sample_post.id})
        data = {
            'author_name': 'John Doe',
            'content': 'Hi'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'content' in response.data
    
    def test_create_comment_whitespace_content(self, api_client, sample_post):
        """Test creating comment with whitespace-only content."""
        url = reverse('blog:comment-create', kwargs={'post_id': sample_post.id})
        data = {
            'author_name': 'John Doe',
            'content': '   '
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'content' in response.data
    
    def test_create_comment_missing_author_name(self, api_client, sample_post):
        """Test creating comment without author name."""
        url = reverse('blog:comment-create', kwargs={'post_id': sample_post.id})
        data = {
            'content': 'This is a test comment.'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'author_name' in response.data
    
    def test_create_comment_missing_content(self, api_client, sample_post):
        """Test creating comment without content."""
        url = reverse('blog:comment-create', kwargs={'post_id': sample_post.id})
        data = {
            'author_name': 'John Doe'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'content' in response.data
    
    def test_create_comment_non_existent_post(self, api_client, non_existent_uuid):
        """Test creating comment for non-existent post."""
        url = reverse('blog:comment-create', kwargs={'post_id': non_existent_uuid})
        data = {
            'author_name': 'John Doe',
            'content': 'This is a test comment.'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_comment_exact_minimum_length(self, api_client, sample_post):
        """Test creating comment with exactly 5 characters."""
        url = reverse('blog:comment-create', kwargs={'post_id': sample_post.id})
        data = {
            'author_name': 'John Doe',
            'content': '12345'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == '12345'
    
    def test_create_comment_strips_whitespace(self, api_client, sample_post):
        """Test that comment content is stripped of whitespace."""
        url = reverse('blog:comment-create', kwargs={'post_id': sample_post.id})
        data = {
            'author_name': 'John Doe',
            'content': '  This is a test comment.  '
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == 'This is a test comment.'
    
    def test_create_multiple_comments_same_post(self, api_client, sample_post):
        """Test creating multiple comments on the same post."""
        url = reverse('blog:comment-create', kwargs={'post_id': sample_post.id})
        
        # Create first comment
        data1 = {
            'author_name': 'John Doe',
            'content': 'This is the first comment.'
        }
        response1 = api_client.post(url, data1, format='json')
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Create second comment
        data2 = {
            'author_name': 'Jane Smith',
            'content': 'This is the second comment.'
        }
        response2 = api_client.post(url, data2, format='json')
        assert response2.status_code == status.HTTP_201_CREATED
        
        # Verify both comments were created
        assert Comment.objects.count() == 2
        comments = Comment.objects.filter(post=sample_post)
        assert comments.count() == 2 