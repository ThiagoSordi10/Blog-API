"""
Cache helpers for blog app.
"""
from django.core.cache import cache
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
import json


class BlogCacheHelper:
    """Helper class for managing blog-related cache operations."""
    
    # Cache keys
    POSTS_LIST_KEY = 'posts_list'
    POST_DETAIL_KEY = 'post_detail_{}'
    POST_COMMENTS_KEY = 'post_comments_{}'
    
    # Cache timeout in seconds (5 minutes)
    CACHE_TIMEOUT = 300
    
    @classmethod
    def get_posts_list(cls):
        """Get cached posts list."""
        try:
            return cache.get(cls.POSTS_LIST_KEY)
        except Exception:
            return None
    
    @classmethod
    def set_posts_list(cls, data):
        """Cache posts list data."""
        try:
            cache.set(cls.POSTS_LIST_KEY, data, cls.CACHE_TIMEOUT)
        except Exception:
            pass  # Silently fail if cache is not available
    
    @classmethod
    def invalidate_posts_list(cls):
        """Invalidate posts list cache."""
        try:
            cache.delete(cls.POSTS_LIST_KEY)
        except Exception:
            pass
    
    @classmethod
    def get_post_detail(cls, post_id):
        """Get cached post detail."""
        try:
            return cache.get(cls.POST_DETAIL_KEY.format(post_id))
        except Exception:
            return None
    
    @classmethod
    def set_post_detail(cls, post_id, data):
        """Cache post detail data."""
        try:
            cache.set(cls.POST_DETAIL_KEY.format(post_id), data, cls.CACHE_TIMEOUT)
        except Exception:
            pass
    
    @classmethod
    def invalidate_post_detail(cls, post_id):
        """Invalidate post detail cache."""
        try:
            cache.delete(cls.POST_DETAIL_KEY.format(post_id))
        except Exception:
            pass
    
    @classmethod
    def get_post_comments(cls, post_id):
        """Get cached post comments."""
        try:
            return cache.get(cls.POST_COMMENTS_KEY.format(post_id))
        except Exception:
            return None
    
    @classmethod
    def set_post_comments(cls, post_id, data):
        """Cache post comments data."""
        try:
            cache.set(cls.POST_COMMENTS_KEY.format(post_id), data, cls.CACHE_TIMEOUT)
        except Exception:
            pass
    
    @classmethod
    def invalidate_post_comments(cls, post_id):
        """Invalidate post comments cache."""
        try:
            cache.delete(cls.POST_COMMENTS_KEY.format(post_id))
        except Exception:
            pass
    
    @classmethod
    def invalidate_all_post_cache(cls, post_id):
        """Invalidate all cache related to a specific post."""
        cls.invalidate_post_detail(post_id)
        cls.invalidate_post_comments(post_id)
        cls.invalidate_posts_list()
    
    @classmethod
    def invalidate_all_cache(cls):
        """Invalidate all blog-related cache."""
        try:
            cache.clear()
        except Exception:
            pass 