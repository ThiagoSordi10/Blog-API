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
    
    def test_create_comment_success(self, api_client, sample_post, sample_user):
        """Test creating a new comment successfully."""
        # Autentica o usuário
        api_client.force_authenticate(user=sample_user)
        
        url = reverse('blog:comment-create', kwargs={'post_id': sample_post.id})
        data = {
            'content': 'This is a test comment with more than 5 characters.'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == data['content']
        assert 'id' in response.data
        assert 'created_at' in response.data
        assert 'author' in response.data
        assert response.data['author']['username'] == sample_user.username
        
        # Verify comment was created in database
        assert Comment.objects.count() == 1
        comment = Comment.objects.first()
        assert comment.post == sample_post
        assert comment.author == sample_user
    
    def test_create_comment_short_content(self, api_client, sample_post, sample_user):
        """Test creating comment with content shorter than 5 characters."""
        # Autentica o usuário
        api_client.force_authenticate(user=sample_user)
        
        url = reverse('blog:comment-create', kwargs={'post_id': sample_post.id})
        data = {
            'content': 'Hi'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'content' in response.data
    
    def test_create_comment_whitespace_content(self, api_client, sample_post, sample_user):
        """Test creating comment with whitespace-only content."""
        # Autentica o usuário
        api_client.force_authenticate(user=sample_user)
        
        url = reverse('blog:comment-create', kwargs={'post_id': sample_post.id})
        data = {
            'content': '   '
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'content' in response.data
    
    def test_create_comment_missing_content(self, api_client, sample_post, sample_user):
        """Test creating comment without content."""
        # Autentica o usuário
        api_client.force_authenticate(user=sample_user)
        
        url = reverse('blog:comment-create', kwargs={'post_id': sample_post.id})
        data = {}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'content' in response.data
    
    def test_create_comment_non_existent_post(self, api_client, non_existent_uuid, sample_user):
        """Test creating comment for non-existent post."""
        # Autentica o usuário
        api_client.force_authenticate(user=sample_user)
        
        url = reverse('blog:comment-create', kwargs={'post_id': non_existent_uuid})
        data = {
            'content': 'This is a test comment.'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_comment_exact_minimum_length(self, api_client, sample_post, sample_user):
        """Test creating comment with exactly 5 characters."""
        # Autentica o usuário
        api_client.force_authenticate(user=sample_user)
        
        url = reverse('blog:comment-create', kwargs={'post_id': sample_post.id})
        data = {
            'content': '12345'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == '12345'
    
    def test_create_comment_strips_whitespace(self, api_client, sample_post, sample_user):
        """Test that comment content is stripped of whitespace."""
        # Autentica o usuário
        api_client.force_authenticate(user=sample_user)
        
        url = reverse('blog:comment-create', kwargs={'post_id': sample_post.id})
        data = {
            'content': '  This is a test comment.  '
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == 'This is a test comment.'
    
    def test_create_multiple_comments_same_post(self, api_client, sample_post, sample_user):
        """Test creating multiple comments on the same post."""
        # Autentica o usuário
        api_client.force_authenticate(user=sample_user)
        
        url = reverse('blog:comment-create', kwargs={'post_id': sample_post.id})
        
        # Create first comment
        data1 = {
            'content': 'This is the first comment.'
        }
        response1 = api_client.post(url, data1, format='json')
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Create second comment
        data2 = {
            'content': 'This is the second comment.'
        }
        response2 = api_client.post(url, data2, format='json')
        assert response2.status_code == status.HTTP_201_CREATED
        
        # Verify both comments were created
        assert Comment.objects.count() == 2
        comments = Comment.objects.filter(post=sample_post)
        assert comments.count() == 2 