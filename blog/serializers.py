from rest_framework import serializers
from .models import BlogPost, Comment


class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be blank.")
        return value.strip()


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'author_name', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_content(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Comment content must have at least 5 characters.")
        return value.strip()


class BlogPostDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'comments']
        read_only_fields = ['id', 'created_at', 'updated_at', 'comments']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be blank.")
        return value.strip()


class BlogPostListSerializer(serializers.ModelSerializer):
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'comment_count']

    def get_comment_count(self, obj):
        return obj.comments.count() 