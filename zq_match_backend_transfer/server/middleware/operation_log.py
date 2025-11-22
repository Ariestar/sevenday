"""
操作日志中间件
"""
import logging
import json
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

logger = logging.getLogger('operation')


class OperationLogMiddleware(MiddlewareMixin):
    """操作日志中间件"""
    
    # 需要记录的操作方法
    LOG_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    # 排除的路径
    EXCLUDE_PATHS = [
        '/admin/',
        '/static/',
        '/media/',
    ]
    
    def process_request(self, request):
        """记录请求开始时间"""
        request.start_time = timezone.now()
        return None
    
    def process_response(self, request, response):
        """记录操作日志"""
        # 检查是否需要记录
        if not self._should_log(request):
            return response
        
        # 计算请求耗时
        if hasattr(request, 'start_time'):
            duration = (timezone.now() - request.start_time).total_seconds()
        else:
            duration = 0
        
        # 获取用户信息
        user_info = 'Anonymous'
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_info = f"{request.user.id}:{request.user.username}"
        
        # 记录日志
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'user': user_info,
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration': f"{duration:.3f}s",
            'ip': self._get_client_ip(request),
        }
        
        # 记录请求参数（POST/PUT/PATCH）
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if request.content_type == 'application/json':
                    body = json.loads(request.body.decode('utf-8'))
                    # 隐藏敏感信息
                    self._hide_sensitive_data(body)
                    log_data['body'] = body
            except:
                pass
        
        logger.info(json.dumps(log_data, ensure_ascii=False))
        
        return response
    
    def _should_log(self, request):
        """判断是否需要记录日志"""
        # 只记录特定方法
        if request.method not in self.LOG_METHODS:
            return False
        
        # 排除特定路径
        for path in self.EXCLUDE_PATHS:
            if request.path.startswith(path):
                return False
        
        return True
    
    def _get_client_ip(self, request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _hide_sensitive_data(self, data):
        """隐藏敏感数据"""
        sensitive_fields = ['password', 'token', 'secret', 'key']
        
        if isinstance(data, dict):
            for key in data:
                if any(field in key.lower() for field in sensitive_fields):
                    data[key] = '***'
                elif isinstance(data[key], dict):
                    self._hide_sensitive_data(data[key])
