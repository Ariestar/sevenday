"""
缓存工具函数
"""
from functools import wraps
from django.core.cache import cache
from django.conf import settings
import hashlib
import json


def cache_response(timeout=300, key_prefix='view'):
    """
    视图缓存装饰器
    
    Args:
        timeout: 缓存超时时间（秒），默认5分钟
        key_prefix: 缓存键前缀
    """
    def decorator(func):
        @wraps(func)
        def wrapper(view_instance, request, *args, **kwargs):
            # 开发环境不使用缓存
            if settings.DEBUG:
                return func(view_instance, request, *args, **kwargs)
            
            # 生成缓存键
            cache_key = _generate_cache_key(
                key_prefix,
                request.path,
                request.GET.dict(),
                request.user.id if request.user.is_authenticated else 'anonymous'
            )
            
            # 尝试从缓存获取
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data
            
            # 执行视图函数
            response = func(view_instance, request, *args, **kwargs)
            
            # 缓存结果
            cache.set(cache_key, response, timeout)
            
            return response
        return wrapper
    return decorator


def invalidate_cache(key_patterns):
    """
    清除匹配模式的缓存
    
    Args:
        key_patterns: 缓存键模式列表
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # 清除相关缓存
            for pattern in key_patterns:
                cache.delete_pattern(pattern)
            
            return result
        return wrapper
    return decorator


def _generate_cache_key(*args):
    """生成缓存键"""
    # 将参数转换为字符串
    key_data = json.dumps(args, sort_keys=True, ensure_ascii=False)
    
    # 使用 MD5 生成哈希
    hash_key = hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    return f"cache:{hash_key}"


def clear_model_cache(model_name):
    """清除特定模型的所有缓存"""
    pattern = f"cache:*{model_name}*"
    try:
        cache.delete_pattern(pattern)
    except AttributeError:
        # 如果缓存后端不支持 delete_pattern，则跳过
        pass
