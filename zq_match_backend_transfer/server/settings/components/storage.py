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
import logging
logger = logging.getLogger(__name__)

ecs_credentials = None
try:
    from server.utils.ecs_credentials import get_sts_credentials_from_ecs, is_ecs_instance
    import requests
    
    # 检查是否在 ECS 实例上
    if is_ecs_instance():
        logger.info("✅ 检测到 ECS 实例，开始获取 STS 凭证...")
        
        # 优先自动检测 RAM 角色，如果检测失败再使用环境变量指定的角色名称
        # 这样可以避免环境变量配置错误导致的问题
        role_name = None
        logger.info("🔍 自动检测 RAM 角色...")
        try:
            role_url = "http://100.100.100.200/latest/meta-data/Ram/security-credentials/"
            role_response = requests.get(role_url, timeout=2)
            if role_response.status_code == 200:
                detected_role = role_response.text.strip()
                if detected_role:
                    role_name = detected_role
                    logger.info(f"✅ 检测到 RAM 角色: {role_name}")
                else:
                    logger.warning("⚠️  ECS 实例未绑定 RAM 角色")
            else:
                logger.warning(f"⚠️  无法获取 RAM 角色，状态码: {role_response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️  获取 RAM 角色失败: {str(e)}")
        
        # 如果自动检测失败，尝试使用环境变量指定的角色名称
        if not role_name:
            env_role_name = config("ALIYUN_OSS_ROLE_NAME", None)
            if env_role_name:
                role_name = env_role_name
                logger.info(f"📌 使用环境变量指定的角色: {role_name}")
            else:
                logger.warning("⚠️  未找到 RAM 角色（自动检测和环境变量都未配置）")
        
        # 获取凭证
        if role_name:
            logger.info(f"🔑 正在获取角色 '{role_name}' 的 STS 凭证...")
            ecs_credentials = get_sts_credentials_from_ecs(role_name=role_name)
            
            if ecs_credentials:
                logger.info(f"✅ 成功获取 STS 凭证（角色: {role_name}）")
            else:
                logger.warning(f"⚠️  无法获取 STS 凭证（角色: {role_name}），将使用环境变量配置")
        else:
            logger.warning("⚠️  未找到 RAM 角色，将使用环境变量配置")
    else:
        logger.info("ℹ️  不在 ECS 实例上，跳过 ECS 凭证获取，将使用环境变量配置")
        
except ImportError as e:
    logger.warning(f"⚠️  无法导入 ECS 凭证模块: {str(e)}，将使用环境变量配置")
except Exception as e:
    logger.error(f"❌ 获取 ECS 凭证时发生异常: {str(e)}")
    import traceback
    logger.debug(traceback.format_exc())
    # 不设置 ecs_credentials = None，让后续代码继续尝试使用环境变量

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
