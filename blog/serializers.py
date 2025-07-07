from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import BlogPost, Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Credenciais inválidas.')
            if not user.is_active:
                raise serializers.ValidationError('Usuário está desativado.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Username e password são obrigatórios.')
        
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError('As senhas não coincidem.')
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class BlogPostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be blank.")
        return value.strip()


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

    def validate_content(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Comment content must have at least 5 characters.")
        return value.strip()


class BlogPostDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at', 'comments']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'comments']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be blank.")
        return value.strip()


class BlogPostListSerializer(serializers.ModelSerializer):
    comment_count = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'comment_count', 'author']

    def get_comment_count(self, obj):
        return obj.comments.count() 