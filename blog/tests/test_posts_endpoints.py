"""
Tests for blog post endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from blog.models import BlogPost
from blog.cache_helpers import BlogCacheHelper


@pytest.mark.django_db
class TestPostsListEndpoint:
    """Tests for GET /api/posts endpoint."""
    
    def test_get_posts_list_empty(self, api_client):
        """Test getting empty posts list."""
        # Limpa o cache para garantir estado limpo
        BlogCacheHelper.invalidate_all_cache()
        
        url = reverse('blog:post-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Verifica se a resposta tem a estrutura de paginação
        assert 'count' in response.data
        assert 'results' in response.data
        assert response.data['count'] == 0
        assert response.data['results'] == []
    
    def test_get_posts_list_with_posts(self, api_client, multiple_posts):
        """Test getting posts list with existing posts."""
        # Limpa o cache para garantir estado limpo
        BlogCacheHelper.invalidate_all_cache()
        
        url = reverse('blog:post-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert len(response.data['results']) == 3
        
        # Check structure
        for post_data in response.data['results']:
            assert 'id' in post_data
            assert 'title' in post_data
            assert 'comment_count' in post_data
            assert 'content' not in post_data  # Should not include content in list
    
    def test_get_posts_list_comment_count(self, api_client, sample_post_with_comments):
        """Test that comment count is correct."""
        # Limpa o cache para garantir estado limpo
        BlogCacheHelper.invalidate_all_cache()
        
        url = reverse('blog:post-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['comment_count'] == 2


@pytest.mark.django_db
class TestPostsCreateEndpoint:
    """Tests for POST /api/posts endpoint."""
    
    def test_create_post_success(self, api_client, sample_user):
        """Test creating a new post successfully."""
        # Limpa o cache para garantir estado limpo
        BlogCacheHelper.invalidate_all_cache()
        
        # Autentica o usuário
        api_client.force_authenticate(user=sample_user)
        
        url = reverse('blog:post-list-create')
        data = {
            'title': 'New Test Post',
            'content': 'This is a new test post content.'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == data['title']
        assert response.data['content'] == data['content']
        assert 'id' in response.data
        assert 'created_at' in response.data
        assert 'updated_at' in response.data
        
        # Verify post was created in database
        assert BlogPost.objects.count() == 1
        post = BlogPost.objects.first()
        assert post.title == data['title']
        assert post.author == sample_user
    
    def test_create_post_blank_title(self, api_client, sample_user):
        """Test creating post with blank title."""
        # Autentica o usuário
        api_client.force_authenticate(user=sample_user)
        
        url = reverse('blog:post-list-create')
        data = {
            'title': '',
            'content': 'This is a test post content.'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data
    
    def test_create_post_missing_title(self, api_client, sample_user):
        """Test creating post without title."""
        # Autentica o usuário
        api_client.force_authenticate(user=sample_user)
        
        url = reverse('blog:post-list-create')
        data = {
            'content': 'This is a test post content.'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data
    
    def test_create_post_missing_content(self, api_client, sample_user):
        """Test creating post without content."""
        # Autentica o usuário
        api_client.force_authenticate(user=sample_user)
        
        url = reverse('blog:post-list-create')
        data = {
            'title': 'Test Post'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'content' in response.data
    
    def test_create_post_whitespace_title(self, api_client, sample_user):
        """Test creating post with whitespace-only title."""
        # Autentica o usuário
        api_client.force_authenticate(user=sample_user)
        
        url = reverse('blog:post-list-create')
        data = {
            'title': '   ',
            'content': 'This is a test post content.'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data


@pytest.mark.django_db
class TestPostDetailEndpoint:
    """Tests for GET /api/posts/{id} endpoint."""
    
    def test_get_post_detail_success(self, api_client, sample_post):
        """Test getting post detail successfully."""
        # Limpa o cache para garantir estado limpo
        BlogCacheHelper.invalidate_all_cache()
        
        url = reverse('blog:post-detail', kwargs={'id': sample_post.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(sample_post.id)
        assert response.data['title'] == sample_post.title
        assert response.data['content'] == sample_post.content
        assert 'comments' in response.data
        assert response.data['comments'] == []
    
    def test_get_post_detail_with_comments(self, api_client, sample_post_with_comments):
        """Test getting post detail with comments."""
        # Limpa o cache para garantir estado limpo
        BlogCacheHelper.invalidate_all_cache()
        
        url = reverse('blog:post-detail', kwargs={'id': sample_post_with_comments.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['comments']) == 2
        
        # Check comment structure
        for comment in response.data['comments']:
            assert 'id' in comment
            assert 'author' in comment
            assert 'content' in comment
            assert 'created_at' in comment
    
    def test_get_post_detail_non_existent(self, api_client, non_existent_uuid):
        """Test getting non-existent post."""
        url = reverse('blog:post-detail', kwargs={'id': non_existent_uuid})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND 