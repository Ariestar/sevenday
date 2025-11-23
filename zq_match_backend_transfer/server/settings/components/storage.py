from server.settings.util import BASE_DIR, config

# region Static files
# https://docs.djangoproject.com/en/2.2/howto/static-files

STATIC_URL = "https://zq-public-oss.oss-cn-hangzhou.aliyuncs.com/zq-auth/backend/static/static/"

STATIC_ROOT = str(BASE_DIR.joinpath("static"))
# endregion

# region 媒体文件
# 直接使用阿里云OSS存储
# OSS配置（支持STS临时访问凭证）
# 优先从ECS元数据服务自动获取STS凭证，如果无法获取则使用环境变量配置

# 尝试从ECS实例元数据服务获取STS临时凭证（如果ECS实例绑定了RAM角色）
# 自动检测ECS实例绑定的RAM角色，无需手动指定
# 如果ECS实例绑定了多个角色，可以通过环境变量 ALIYUN_OSS_ROLE_NAME 指定
try:
    from server.utils.ecs_credentials import get_sts_credentials_from_ecs
    # 优先使用环境变量指定的角色名称，否则自动检测
    role_name = config("ALIYUN_OSS_ROLE_NAME", None)
    ecs_credentials = get_sts_credentials_from_ecs(role_name=role_name)
except Exception:
    ecs_credentials = None

# OSS配置：优先使用ECS自动获取的凭证，否则使用环境变量
ALIYUN_OSS = {
    # 优先使用ECS自动获取的STS凭证，如果没有则使用环境变量
    "ACCESS_KEY_ID": (
        ecs_credentials.get('ACCESS_KEY_ID') 
        if ecs_credentials and ecs_credentials.get('ACCESS_KEY_ID')
        else config("ALIYUN_OSS_ACCESS_KEY_ID", "")
    ),
    "ACCESS_KEY_SECRET": (
        ecs_credentials.get('ACCESS_KEY_SECRET')
        if ecs_credentials and ecs_credentials.get('ACCESS_KEY_SECRET')
        else config("ALIYUN_OSS_ACCESS_KEY_SECRET", "")
    ),
    "SECURITY_TOKEN": (
        ecs_credentials.get('SECURITY_TOKEN')
        if ecs_credentials and ecs_credentials.get('SECURITY_TOKEN')
        else config("ALIYUN_OSS_SECURITY_TOKEN", "")
    ),
    "ENDPOINT": config("ALIYUN_OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com"),  # 北京地域
    "BUCKET_NAME": config("ALIYUN_OSS_BUCKET_NAME", "zq-match"),  # bucket名称：zq-match
    "ROLE_NAME": config("ALIYUN_OSS_ROLE_NAME", None),  # RAM角色名称（可选，如果不指定则自动检测）
    "URL_EXPIRE_SECOND": 60 * 60 * 24 * 30,
    "TOKEN_EXPIRE_SECOND": 60,
    "MAX_SIZE_MB": 100,
}

# 使用阿里云OSS存储后端
# 使用自定义的OSS存储后端（基于oss2）
DEFAULT_FILE_STORAGE = "server.utils.oss_storage.AliyunOSSStorage"

# OSS的访问URL（根据Bucket和Endpoint构建）
bucket_name = ALIYUN_OSS.get("BUCKET_NAME", "")
endpoint = ALIYUN_OSS.get("ENDPOINT", "oss-cn-beijing.aliyuncs.com")
# 移除endpoint中的http://或https://前缀
if endpoint.startswith('http://'):
    endpoint = endpoint.replace('http://', '')
elif endpoint.startswith('https://'):
    endpoint = endpoint.replace('https://', '')

if bucket_name:
    # 如果配置了Bucket名称，使用Bucket域名
    MEDIA_URL = f"https://{bucket_name}.{endpoint}/"
else:
    # 否则使用默认的OSS域名格式
    MEDIA_URL = f"https://{endpoint}/"
# endregion
