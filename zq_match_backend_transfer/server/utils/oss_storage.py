"""
阿里云OSS存储后端（支持STS临时访问凭证）
自动从ECS服务端获取V4签名凭证信息上传文件到OSS
"""
import oss2
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)


@deconstructible
class AliyunOSSStorage(Storage):
    """阿里云OSS存储后端（支持STS临时访问凭证，自动从ECS获取）"""
    
    def __init__(self):
        self.oss_config = getattr(settings, 'ALIYUN_OSS', {})
        self.endpoint = self.oss_config.get('ENDPOINT', 'oss-cn-beijing.aliyuncs.com')
        self.bucket_name = self.oss_config.get('BUCKET_NAME', '')
        
        # 验证必要配置
        if not self.bucket_name:
            raise ValueError("阿里云OSS配置不完整，请检查ALIYUN_OSS配置（需要BUCKET_NAME）")
        
        # 初始化凭证（支持自动刷新）
        self._refresh_credentials()
        
        # 验证凭证
        if not all([self.access_key_id, self.access_key_secret]):
            raise ValueError("阿里云OSS凭证获取失败，请检查ECS RAM角色绑定或环境变量配置")
        
        # 构建endpoint URL（oss2需要完整的endpoint URL）
        if not self.endpoint.startswith('http'):
            endpoint_url = f"https://{self.endpoint}"
        else:
            endpoint_url = self.endpoint
        
        # 初始化OSS客户端
        self._init_bucket(endpoint_url)
    
    def _refresh_credentials(self):
        """刷新凭证（优先从ECS获取，否则使用配置）"""
        # 尝试从ECS元数据服务获取最新凭证（自动检测RAM角色）
        try:
            from server.utils.ecs_credentials import get_sts_credentials_from_ecs
            from django.conf import settings
            # 优先使用配置中指定的角色名称，否则自动检测
            role_name = self.oss_config.get('ROLE_NAME', None)
            ecs_credentials = get_sts_credentials_from_ecs(role_name=role_name)
            
            if ecs_credentials and all(ecs_credentials.values()):
                # 使用ECS获取的凭证
                self.access_key_id = ecs_credentials.get('ACCESS_KEY_ID')
                self.access_key_secret = ecs_credentials.get('ACCESS_KEY_SECRET')
                self.security_token = ecs_credentials.get('SECURITY_TOKEN')
                # 记录使用的角色名称（从ecs_credentials中获取，如果有的话）
                logger.info("使用从ECS元数据服务获取的STS临时凭证（自动检测RAM角色）")
                return
        except Exception as e:
            logger.debug(f"从ECS获取凭证失败，使用配置的凭证: {str(e)}")
        
        # 使用配置中的凭证
        self.access_key_id = self.oss_config.get('ACCESS_KEY_ID', '')
        self.access_key_secret = self.oss_config.get('ACCESS_KEY_SECRET', '')
        self.security_token = self.oss_config.get('SECURITY_TOKEN', '')
        
        if self.security_token:
            logger.info("使用配置的STS临时凭证")
        else:
            logger.info("使用配置的永久AccessKey")
    
    def _init_bucket(self, endpoint_url):
        """初始化OSS Bucket客户端"""
        # 如果提供了SECURITY_TOKEN，使用STS临时凭证（V4签名）
        # 否则使用永久AccessKey
        if self.security_token:
            # 使用STS临时访问凭证（V4签名）
            auth = oss2.StsAuth(self.access_key_id, self.access_key_secret, self.security_token)
        else:
            # 使用永久AccessKey
            auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        
        self.bucket = oss2.Bucket(auth, endpoint_url, self.bucket_name)
    
    def _open(self, name, mode='rb'):
        """打开文件"""
        try:
            obj = self.bucket.get_object(name)
            return ContentFile(obj.read())
        except oss2.exceptions.NoSuchKey:
            raise FileNotFoundError(f"文件不存在: {name}")
        except Exception as e:
            logger.error(f"从OSS读取文件失败: {name}, 错误: {str(e)}")
            raise IOError(f"读取OSS文件失败: {str(e)}")
    
    def _save(self, name, content):
        """保存文件到OSS（使用STS临时凭证或永久AccessKey，支持自动刷新凭证）"""
        # 读取文件内容
        content.seek(0)
        file_content = content.read()
        
        # 上传到OSS（如果失败可能是凭证过期，尝试刷新后重试）
        max_retries = 2
        for attempt in range(max_retries):
            try:
                # 使用put_object上传文件
                # oss2会自动使用配置的认证信息（STS或永久AccessKey）进行V4签名
                result = self.bucket.put_object(name, file_content)
                logger.info(f"文件上传成功: {name}, ETag: {result.etag}")
                return name
            except (oss2.exceptions.InvalidAccessKeyId, oss2.exceptions.SignatureDoesNotMatch) as e:
                # 如果是凭证相关错误，尝试刷新凭证后重试
                if attempt < max_retries - 1:
                    logger.warning(f"OSS凭证可能过期，尝试刷新凭证后重试: {str(e)}")
                    try:
                        self._refresh_credentials()
                        # 重新初始化bucket
                        if not self.endpoint.startswith('http'):
                            endpoint_url = f"https://{self.endpoint}"
                        else:
                            endpoint_url = self.endpoint
                        self._init_bucket(endpoint_url)
                        continue  # 重试
                    except Exception as refresh_error:
                        logger.error(f"刷新凭证失败: {str(refresh_error)}")
                
                # 最后一次尝试失败，抛出异常
                logger.error(f"OSS AccessKey无效或签名不匹配: {name}, 错误: {str(e)}")
                raise IOError(f"OSS凭证验证失败，请检查配置: {str(e)}")
            except oss2.exceptions.AccessDenied as e:
                logger.error(f"OSS访问被拒绝: {name}, 错误: {str(e)}")
                raise IOError(f"OSS访问被拒绝，请检查凭证权限: {str(e)}")
            except Exception as e:
                logger.error(f"上传文件到OSS失败: {name}, 错误: {str(e)}", exc_info=True)
                raise IOError(f"上传文件到OSS失败: {str(e)}")
    
    def exists(self, name):
        """检查文件是否存在"""
        try:
            return self.bucket.object_exists(name)
        except Exception as e:
            logger.error(f"检查OSS文件是否存在失败: {name}, 错误: {str(e)}")
            return False
    
    def url(self, name):
        """获取文件URL"""
        # 构建OSS访问URL
        if not self.endpoint.startswith('http'):
            base_url = f"https://{self.bucket_name}.{self.endpoint}"
        else:
            base_url = f"https://{self.bucket_name}.{self.endpoint.replace('https://', '').replace('http://', '')}"
        
        return urljoin(base_url + '/', name)
    
    def delete(self, name):
        """删除文件"""
        try:
            self.bucket.delete_object(name)
            logger.info(f"文件删除成功: {name}")
        except Exception as e:
            logger.error(f"删除OSS文件失败: {name}, 错误: {str(e)}")
            raise IOError(f"删除OSS文件失败: {str(e)}")
    
    def size(self, name):
        """获取文件大小"""
        try:
            meta = self.bucket.head_object(name)
            return meta.content_length
        except oss2.exceptions.NoSuchKey:
            raise FileNotFoundError(f"文件不存在: {name}")
        except Exception as e:
            logger.error(f"获取OSS文件大小失败: {name}, 错误: {str(e)}")
            raise IOError(f"获取文件大小失败: {str(e)}")

