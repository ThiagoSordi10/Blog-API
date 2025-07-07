import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'password_confirm': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User'
    }


@pytest.fixture
def login_data():
    return {
        'username': 'testuser',
        'password': 'testpass123'
    }


@pytest.fixture
def authenticated_client(api_client, user_data):
    """Cria um usuário e retorna um cliente autenticado"""
    # Registra o usuário
    response = api_client.post('/api/auth/register/', user_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    # Faz login
    login_response = api_client.post('/api/auth/login/', {
        'username': user_data['username'],
        'password': user_data['password']
    })
    assert login_response.status_code == status.HTTP_200_OK
    
    # Adiciona o token ao cliente
    token = login_response.data['token']
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    
    return api_client


@pytest.mark.django_db
class TestRegisterEndpoint:
    """Testes para o endpoint de registro"""
    
    def test_register_success(self, api_client, user_data):
        """Testa registro bem-sucedido"""
        response = api_client.post('/api/auth/register/', user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username=user_data['username']).exists()
        
        user = User.objects.get(username=user_data['username'])
        assert user.email == user_data['email']
        assert user.check_password(user_data['password'])
    
    def test_register_password_mismatch(self, api_client, user_data):
        """Testa registro com senhas diferentes"""
        user_data['password_confirm'] = 'differentpass'
        response = api_client.post('/api/auth/register/', user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'senhas não coincidem' in str(response.data).lower()
    
    def test_register_duplicate_username(self, api_client, user_data):
        """Testa registro com username duplicado"""
        # Primeiro registro
        response1 = api_client.post('/api/auth/register/', user_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Segundo registro com mesmo username
        response2 = api_client.post('/api/auth/register/', user_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginEndpoint:
    """Testes para o endpoint de login"""
    
    def test_login_success(self, api_client, user_data, login_data):
        """Testa login bem-sucedido"""
        # Registra o usuário primeiro
        api_client.post('/api/auth/register/', user_data)
        
        # Faz login
        response = api_client.post('/api/auth/login/', login_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data
        assert 'user' in response.data
        assert response.data['user']['username'] == login_data['username']
    
    def test_login_invalid_credentials(self, api_client):
        """Testa login com credenciais inválidas"""
        response = api_client.post('/api/auth/login/', {
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'credenciais inválidas' in str(response.data).lower()
    
    def test_login_missing_fields(self, api_client):
        """Testa login com campos faltando"""
        response = api_client.post('/api/auth/login/', {
            'username': 'testuser'
            # password faltando
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProfileEndpoint:
    """Testes para o endpoint de perfil"""
    
    def test_profile_authenticated(self, authenticated_client):
        """Testa acesso ao perfil com autenticação"""
        response = authenticated_client.get('/api/auth/profile/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'username' in response.data
        assert 'email' in response.data
    
    def test_profile_unauthenticated(self, api_client):
        """Testa acesso ao perfil sem autenticação"""
        response = api_client.get('/api/auth/profile/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAuthenticatedEndpoints:
    """Testes para endpoints que requerem autenticação"""
    
    def test_create_post_authenticated(self, authenticated_client):
        """Testa criação de post com autenticação"""
        post_data = {
            'title': 'Test Post',
            'content': 'Test content'
        }
        
        response = authenticated_client.post('/api/posts/', post_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == post_data['title']
        assert response.data['content'] == post_data['content']
        assert 'author' in response.data
        assert response.data['author']['username'] == 'testuser'
    
    def test_create_post_unauthenticated(self, api_client):
        """Testa criação de post sem autenticação"""
        post_data = {
            'title': 'Test Post',
            'content': 'Test content'
        }
        
        response = api_client.post('/api/posts/', post_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_comment_authenticated(self, authenticated_client):
        """Testa criação de comentário com autenticação"""
        # Primeiro cria um post
        post_data = {'title': 'Test Post', 'content': 'Test content'}
        post_response = authenticated_client.post('/api/posts/', post_data)
        post_id = post_response.data['id']
        
        # Cria comentário
        comment_data = {'content': 'Test comment'}
        response = authenticated_client.post(f'/api/posts/{post_id}/comments/', comment_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == comment_data['content']
        assert 'author' in response.data
        assert response.data['author']['username'] == 'testuser'
    
    def test_create_comment_unauthenticated(self, api_client):
        """Testa criação de comentário sem autenticação"""
        # Primeiro cria um usuário e post para ter um post_id válido
        client = APIClient()
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Registra e faz login
        client.post('/api/auth/register/', user_data)
        login_response = client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        token = login_response.data['token']
        client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        # Cria post
        post_data = {'title': 'Test Post', 'content': 'Test content'}
        post_response = client.post('/api/posts/', post_data)
        post_id = post_response.data['id']
        
        # Remove autenticação
        client.credentials()
        
        # Tenta criar comentário sem autenticação
        comment_data = {'content': 'Test comment'}
        response = client.post(f'/api/posts/{post_id}/comments/', comment_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPublicEndpoints:
    """Testes para endpoints públicos"""
    
    def test_list_posts_unauthenticated(self, api_client):
        """Testa listagem de posts sem autenticação"""
        response = api_client.get('/api/posts/')
        
        assert response.status_code == status.HTTP_200_OK
        # Verifica se a resposta tem a estrutura de paginação
        assert 'count' in response.data
        assert 'results' in response.data
    
    def test_retrieve_post_unauthenticated(self, api_client):
        """Testa recuperação de post específico sem autenticação"""
        # Primeiro cria um post autenticado
        client = APIClient()
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        client.post('/api/auth/register/', user_data)
        login_response = client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        token = login_response.data['token']
        client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        post_data = {'title': 'Test Post', 'content': 'Test content'}
        post_response = client.post('/api/posts/', post_data)
        post_id = post_response.data['id']
        
        # Remove autenticação e tenta acessar o post
        client.credentials()
        response = client.get(f'/api/posts/{post_id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == post_data['title'] 