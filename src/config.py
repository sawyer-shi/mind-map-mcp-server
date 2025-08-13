"""
Configuration Management | 配置管理
=====================================

Centralized configuration management for the Mind Map MCP Server.
思维导图MCP服务器的集中配置管理。
"""

import os
import re


def get_env(key: str, default: str = "", cast_type: type = str):
    """Get environment variable with type casting | 获取环境变量并进行类型转换"""
    value = os.getenv(key, default)
    if cast_type == bool:
        return value.lower() in ('true', '1', 'yes', 'on')
    elif cast_type == int:
        try:
            return int(value)
        except ValueError:
            return int(default) if default else 0
    return cast_type(value)


def expand_env_vars(value: str) -> str:
    """
    Expand environment variables in string | 展开字符串中的环境变量
    Supports ${VAR} syntax | 支持${VAR}语法
    """
    if not isinstance(value, str):
        return value
    
    # Pattern to match ${VAR} syntax | 匹配${VAR}语法的模式
    pattern = r'\$\{([^}]+)\}'
    
    def replace_var(match):
        var_name = match.group(1)
        return os.getenv(var_name, match.group(0))  # Return original if not found
    
    return re.sub(pattern, replace_var, value)


def get_env_expanded(key: str, default: str = "", cast_type: type = str):
    """
    Get environment variable with expansion and type casting | 获取带展开和类型转换的环境变量
    """
    value = get_env(key, default, str)  # Always get as string first
    expanded_value = expand_env_vars(value)
    
    if cast_type == bool:
        return expanded_value.lower() in ('true', '1', 'yes', 'on')
    elif cast_type == int:
        try:
            return int(expanded_value)
        except ValueError:
            return int(default) if default else 0
    return cast_type(expanded_value)


class Config:
    """
    Configuration Management Class | 配置管理类
    
    Centralized configuration management for the Mind Map MCP Server.
    思维导图MCP服务器的集中配置管理。
    """
    
    # Server configuration | 服务器配置
    HOST = get_env("HOST", "0.0.0.0")
    LOCAL_HOST = get_env("LOCAL_HOST", "127.0.0.1")
    
    # Port configuration | 端口配置
    STREAMABLE_PORT = get_env("STREAMABLE_PORT", "8091", int)
    STATIC_FILE_PORT = get_env("STATIC_FILE_PORT", "8090", int)
    FASTMCP_INTERNAL_PORT = get_env("FASTMCP_INTERNAL_PORT", "8000", int)
    
    # Debug configuration | 调试配置
    DEBUG = get_env("DEBUG", "false", bool)
    LOG_LEVEL = get_env("LOG_LEVEL", "INFO")
    
    # Image quality settings | 图片质量设置
    IMAGE_QUALITY = get_env("IMAGE_QUALITY", "high")
    DEVICE_SCALE_FACTOR = get_env("DEVICE_SCALE_FACTOR", "2.0", float)
    BASE_VIEWPORT_WIDTH = get_env("BASE_VIEWPORT_WIDTH", "1200", int)
    BASE_VIEWPORT_HEIGHT = get_env("BASE_VIEWPORT_HEIGHT", "800", int)
    MAX_VIEWPORT_WIDTH = get_env("MAX_VIEWPORT_WIDTH", "2400", int)
    MAX_VIEWPORT_HEIGHT = get_env("MAX_VIEWPORT_HEIGHT", "1600", int)
    
    # Directory configuration | 目录配置
    HOST_TEMP_PATH = get_env("HOST_TEMP_PATH", "./temp")
    HOST_OUTPUT_PATH = get_env("HOST_OUTPUT_PATH", "./output")
    HOST_LOG_PATH = get_env("HOST_LOG_PATH", "./logs")
    
    # Storage configuration | 存储配置
    STORAGE_TYPE = get_env("STORAGE_TYPE", "local")
    
    # Local storage configuration | 本地存储配置
    LOCAL_STORAGE_URL_PREFIX = get_env_expanded("LOCAL_STORAGE_URL_PREFIX", f"http://{LOCAL_HOST}:{STATIC_FILE_PORT}/output")
    
    # Aliyun OSS configuration | 阿里云OSS配置
    ALIYUN_OSS_ACCESS_KEY_ID = get_env("ALIYUN_OSS_ACCESS_KEY_ID", "")
    ALIYUN_OSS_ACCESS_KEY_SECRET = get_env("ALIYUN_OSS_ACCESS_KEY_SECRET", "")
    ALIYUN_OSS_ENDPOINT = get_env("ALIYUN_OSS_ENDPOINT", "")
    ALIYUN_OSS_BUCKET_NAME = get_env("ALIYUN_OSS_BUCKET_NAME", "")
    ALIYUN_OSS_REGION = get_env("ALIYUN_OSS_REGION", "")
    ALIYUN_OSS_URL_PREFIX = get_env("ALIYUN_OSS_URL_PREFIX", "")
    
    # Huawei OceanStor configuration | 华为OceanStor配置
    HUAWEI_ACCESS_KEY_ID = get_env("HUAWEI_ACCESS_KEY_ID", "")
    HUAWEI_SECRET_ACCESS_KEY = get_env("HUAWEI_SECRET_ACCESS_KEY", "")
    HUAWEI_ENDPOINT = get_env("HUAWEI_ENDPOINT", "")
    HUAWEI_BUCKET_NAME = get_env("HUAWEI_BUCKET_NAME", "")
    HUAWEI_REGION = get_env("HUAWEI_REGION", "")
    HUAWEI_URL_PREFIX = get_env("HUAWEI_URL_PREFIX", "")
    
    # MinIO configuration | MinIO配置
    MINIO_ENDPOINT = get_env_expanded("MINIO_ENDPOINT", f"{LOCAL_HOST}:9000")
    MINIO_ACCESS_KEY = get_env("MINIO_ACCESS_KEY", "")
    MINIO_SECRET_KEY = get_env("MINIO_SECRET_KEY", "")
    MINIO_BUCKET_NAME = get_env("MINIO_BUCKET_NAME", "")
    MINIO_SECURE = get_env("MINIO_SECURE", "false", bool)
    MINIO_URL_PREFIX = get_env_expanded("MINIO_URL_PREFIX", f"http://{LOCAL_HOST}:9000/mindmaps")
    
    # Amazon S3 configuration | Amazon S3配置
    AWS_ACCESS_KEY_ID = get_env("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = get_env("AWS_SECRET_ACCESS_KEY", "")
    AWS_DEFAULT_REGION = get_env("AWS_DEFAULT_REGION", "")
    AWS_S3_BUCKET_NAME = get_env("AWS_S3_BUCKET_NAME", "")
    AWS_S3_URL_PREFIX = get_env("AWS_S3_URL_PREFIX", "")
    
    # Azure Blob Storage configuration | Azure Blob存储配置
    AZURE_STORAGE_ACCOUNT_NAME = get_env("AZURE_STORAGE_ACCOUNT_NAME", "")
    AZURE_STORAGE_ACCOUNT_KEY = get_env("AZURE_STORAGE_ACCOUNT_KEY", "")
    AZURE_STORAGE_CONTAINER_NAME = get_env("AZURE_STORAGE_CONTAINER_NAME", "")
    AZURE_STORAGE_URL_PREFIX = get_env("AZURE_STORAGE_URL_PREFIX", "")
    
    # Google Cloud Storage configuration | Google Cloud存储配置
    GCS_PROJECT_ID = get_env("GCS_PROJECT_ID", "")
    GCS_BUCKET_NAME = get_env("GCS_BUCKET_NAME", "")
    GCS_CREDENTIALS_FILE = get_env("GCS_CREDENTIALS_FILE", "")
    GCS_CREDENTIALS_JSON = get_env("GCS_CREDENTIALS_JSON", "")
    GCS_URL_PREFIX = get_env("GCS_URL_PREFIX", "")