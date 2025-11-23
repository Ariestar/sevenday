"""
从ECS实例元数据服务获取STS临时凭证
"""
import requests
import json
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# ECS元数据服务地址
ECS_METADATA_BASE_URL = "http://100.100.100.200/latest/meta-data"
ECS_METADATA_TIMEOUT = 2  # 2秒超时


def get_sts_credentials_from_ecs(role_name: Optional[str] = None) -> Optional[Dict[str, str]]:
    """
    从ECS实例元数据服务获取STS临时凭证
    
    Args:
        role_name: RAM角色名称，如果为None则自动获取默认角色
    
    Returns:
        包含ACCESS_KEY_ID、ACCESS_KEY_SECRET、SECURITY_TOKEN的字典，如果获取失败返回None
    """
    try:
        # 如果没有指定角色名，先获取默认角色
        if not role_name:
            role_url = f"{ECS_METADATA_BASE_URL}/Ram/security-credentials/"
            try:
                role_response = requests.get(role_url, timeout=ECS_METADATA_TIMEOUT)
                if role_response.status_code == 200:
                    role_name = role_response.text.strip()
                    if not role_name:
                        logger.debug("ECS实例未绑定RAM角色")
                        return None
                else:
                    logger.debug(f"无法获取RAM角色名称，状态码: {role_response.status_code}")
                    return None
            except requests.exceptions.RequestException as e:
                logger.debug(f"无法连接到ECS元数据服务获取角色名称: {str(e)}")
                return None
        
        # 获取STS临时凭证
        credentials_url = f"{ECS_METADATA_BASE_URL}/Ram/security-credentials/{role_name}"
        try:
            response = requests.get(credentials_url, timeout=ECS_METADATA_TIMEOUT)
            
            if response.status_code == 200:
                credentials_data = response.json()
                
                # 检查返回的Code字段
                if credentials_data.get('Code') != 'Success':
                    logger.warning(f"ECS元数据服务返回错误: {credentials_data.get('Code')}")
                    return None
                
                # 提取凭证信息
                credentials = {
                    'ACCESS_KEY_ID': credentials_data.get('AccessKeyId'),
                    'ACCESS_KEY_SECRET': credentials_data.get('AccessKeySecret'),
                    'SECURITY_TOKEN': credentials_data.get('SecurityToken'),
                }
                
                # 验证凭证完整性
                if all(credentials.values()):
                    logger.info(f"成功从ECS元数据服务获取STS凭证，角色: {role_name}")
                    logger.debug(f"凭证过期时间: {credentials_data.get('Expiration', 'Unknown')}")
                    return credentials
                else:
                    logger.warning("从ECS获取的STS凭证不完整")
                    return None
            else:
                logger.debug(f"无法获取STS凭证，状态码: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.debug(f"无法连接到ECS元数据服务获取凭证: {str(e)}")
            return None
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"解析ECS元数据服务响应失败: {str(e)}")
            return None
            
    except Exception as e:
        logger.debug(f"获取ECS STS凭证时发生异常: {str(e)}")
        return None


def is_ecs_instance() -> bool:
    """
    检查当前是否运行在ECS实例上
    
    Returns:
        如果是ECS实例返回True，否则返回False
    """
    try:
        # 尝试访问ECS元数据服务
        response = requests.get(
            f"{ECS_METADATA_BASE_URL}/instance-id",
            timeout=ECS_METADATA_TIMEOUT
        )
        return response.status_code == 200
    except Exception:
        return False

