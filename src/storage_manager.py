"""
Storage Manager | 存储管理器
===============================

Multi-cloud storage manager for mind map files.
支持多种云存储的思维导图文件存储管理器。
"""

import os
import time
from pathlib import Path
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from config import Config


class StorageProvider(ABC):
    """
    Abstract storage provider interface | 抽象存储提供者接口
    """
    
    @abstractmethod
    async def upload_file(self, file_path: str, remote_path: str) -> Dict[str, Any]:
        """
        Upload file to storage | 上传文件到存储
        
        Args:
            file_path: Local file path
            remote_path: Remote file path
            
        Returns:
            Dict containing success status and URL
        """
        pass
    
    @abstractmethod
    def get_file_url(self, remote_path: str) -> str:
        """
        Get public URL for file | 获取文件的公开URL
        
        Args:
            remote_path: Remote file path
            
        Returns:
            Public URL string
        """
        pass


class LocalStorageProvider(StorageProvider):
    """
    Local storage provider | 本地存储提供者
    """
    
    def __init__(self, output_dir: Path, url_prefix: str):
        self.output_dir = output_dir
        self.url_prefix = url_prefix
        # Ensure output directory exists | 确保输出目录存在
        self.output_dir.mkdir(exist_ok=True)
    
    async def upload_file(self, file_path: str, remote_path: str) -> Dict[str, Any]:
        """
        Save file to local output directory | 保存文件到本地输出目录
        """
        try:
            source_path = Path(file_path)
            target_path = self.output_dir / remote_path
            
            # Ensure target directory exists | 确保目标目录存在
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file to output directory | 复制文件到输出目录
            import shutil
            shutil.copy2(source_path, target_path)
            
            return {
                "success": True,
                "url": self.get_file_url(remote_path),
                "message": f"File saved locally: {target_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "url": None,
                "message": f"Local storage error: {str(e)}"
            }
    
    def get_file_url(self, remote_path: str) -> str:
        """
        Get local file URL | 获取本地文件URL
        """
        return f"{self.url_prefix.rstrip('/')}/{remote_path}"


class AliyunOSSProvider(StorageProvider):
    """
    Aliyun OSS storage provider | 阿里云OSS存储提供者
    """
    
    def __init__(self):
        try:
            import oss2
            
            auth = oss2.Auth(Config.ALIYUN_OSS_ACCESS_KEY_ID, Config.ALIYUN_OSS_ACCESS_KEY_SECRET)
            self.bucket = oss2.Bucket(auth, Config.ALIYUN_OSS_ENDPOINT, Config.ALIYUN_OSS_BUCKET_NAME)
            self.url_prefix = Config.ALIYUN_OSS_URL_PREFIX
            
        except ImportError:
            raise ImportError("Please install oss2: pip install oss2")
        except Exception as e:
            raise Exception(f"Failed to initialize Aliyun OSS: {str(e)}")
    
    async def upload_file(self, file_path: str, remote_path: str) -> Dict[str, Any]:
        """
        Upload file to Aliyun OSS | 上传文件到阿里云OSS
        """
        try:
            # Upload file | 上传文件
            result = self.bucket.put_object_from_file(remote_path, file_path)
            
            if result.status == 200:
                return {
                    "success": True,
                    "url": self.get_file_url(remote_path),
                    "message": f"File uploaded to Aliyun OSS: {remote_path}"
                }
            else:
                return {
                    "success": False,
                    "url": None,
                    "message": f"Aliyun OSS upload failed with status: {result.status}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "url": None,
                "message": f"Aliyun OSS error: {str(e)}"
            }
    
    def get_file_url(self, remote_path: str) -> str:
        """
        Get Aliyun OSS file URL | 获取阿里云OSS文件URL
        """
        return f"{self.url_prefix.rstrip('/')}/{remote_path}"


class HuaweiOceanStorProvider(StorageProvider):
    """
    Huawei OceanStor storage provider | 华为OceanStor存储提供者
    """
    
    def __init__(self):
        try:
            from obs import ObsClient
            
            self.client = ObsClient(
                access_key_id=Config.HUAWEI_ACCESS_KEY_ID,
                secret_access_key=Config.HUAWEI_SECRET_ACCESS_KEY,
                server=Config.HUAWEI_ENDPOINT
            )
            self.bucket_name = Config.HUAWEI_BUCKET_NAME
            self.url_prefix = Config.HUAWEI_URL_PREFIX
            
        except ImportError:
            raise ImportError("Please install esdk-obs-python: pip install esdk-obs-python")
        except Exception as e:
            raise Exception(f"Failed to initialize Huawei OceanStor: {str(e)}")
    
    async def upload_file(self, file_path: str, remote_path: str) -> Dict[str, Any]:
        """
        Upload file to Huawei OceanStor | 上传文件到华为OceanStor
        """
        try:
            # Upload file | 上传文件
            resp = self.client.putFile(self.bucket_name, remote_path, file_path)
            
            if resp.status < 300:
                return {
                    "success": True,
                    "url": self.get_file_url(remote_path),
                    "message": f"File uploaded to Huawei OceanStor: {remote_path}"
                }
            else:
                return {
                    "success": False,
                    "url": None,
                    "message": f"Huawei OceanStor upload failed: {resp.errorMessage}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "url": None,
                "message": f"Huawei OceanStor error: {str(e)}"
            }
    
    def get_file_url(self, remote_path: str) -> str:
        """
        Get Huawei OceanStor file URL | 获取华为OceanStor文件URL
        """
        return f"{self.url_prefix.rstrip('/')}/{remote_path}"


class MinIOProvider(StorageProvider):
    """
    MinIO storage provider | MinIO存储提供者
    """
    
    def __init__(self):
        try:
            from minio import Minio
            
            self.client = Minio(
                Config.MINIO_ENDPOINT,
                access_key=Config.MINIO_ACCESS_KEY,
                secret_key=Config.MINIO_SECRET_KEY,
                secure=Config.MINIO_SECURE
            )
            self.bucket_name = Config.MINIO_BUCKET_NAME
            self.url_prefix = Config.MINIO_URL_PREFIX
            
            # Create bucket if it doesn't exist | 如果桶不存在则创建
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
            
        except ImportError:
            raise ImportError("Please install minio: pip install minio")
        except Exception as e:
            raise Exception(f"Failed to initialize MinIO: {str(e)}")
    
    async def upload_file(self, file_path: str, remote_path: str) -> Dict[str, Any]:
        """
        Upload file to MinIO | 上传文件到MinIO
        """
        try:
            # Upload file | 上传文件
            self.client.fput_object(self.bucket_name, remote_path, file_path)
            
            return {
                "success": True,
                "url": self.get_file_url(remote_path),
                "message": f"File uploaded to MinIO: {remote_path}"
            }
                
        except Exception as e:
            return {
                "success": False,
                "url": None,
                "message": f"MinIO error: {str(e)}"
            }
    
    def get_file_url(self, remote_path: str) -> str:
        """
        Get MinIO file URL | 获取MinIO文件URL
        """
        return f"{self.url_prefix.rstrip('/')}/{remote_path}"


class AmazonS3Provider(StorageProvider):
    """
    Amazon S3 storage provider | Amazon S3存储提供者
    """
    
    def __init__(self):
        try:
            import boto3
            
            self.client = boto3.client(
                's3',
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                region_name=Config.AWS_DEFAULT_REGION
            )
            self.bucket_name = Config.AWS_S3_BUCKET_NAME
            self.url_prefix = Config.AWS_S3_URL_PREFIX
            
        except ImportError:
            raise ImportError("Please install boto3: pip install boto3")
        except Exception as e:
            raise Exception(f"Failed to initialize Amazon S3: {str(e)}")
    
    async def upload_file(self, file_path: str, remote_path: str) -> Dict[str, Any]:
        """
        Upload file to Amazon S3 | 上传文件到Amazon S3
        """
        try:
            # Upload file | 上传文件
            self.client.upload_file(file_path, self.bucket_name, remote_path)
            
            return {
                "success": True,
                "url": self.get_file_url(remote_path),
                "message": f"File uploaded to Amazon S3: {remote_path}"
            }
                
        except Exception as e:
            return {
                "success": False,
                "url": None,
                "message": f"Amazon S3 error: {str(e)}"
            }
    
    def get_file_url(self, remote_path: str) -> str:
        """
        Get Amazon S3 file URL | 获取Amazon S3文件URL
        """
        return f"{self.url_prefix.rstrip('/')}/{remote_path}"


class AzureBlobProvider(StorageProvider):
    """
    Azure Blob Storage provider | Azure Blob存储提供者
    """
    
    def __init__(self):
        try:
            from azure.storage.blob import BlobServiceClient
            
            self.client = BlobServiceClient(
                account_url=f"https://{Config.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
                credential=Config.AZURE_STORAGE_ACCOUNT_KEY
            )
            self.container_name = Config.AZURE_STORAGE_CONTAINER_NAME
            self.url_prefix = Config.AZURE_STORAGE_URL_PREFIX
            
            # Create container if it doesn't exist | 如果容器不存在则创建
            try:
                self.client.create_container(self.container_name)
            except Exception:
                pass  # Container may already exist | 容器可能已存在
            
        except ImportError:
            raise ImportError("Please install azure-storage-blob: pip install azure-storage-blob")
        except Exception as e:
            raise Exception(f"Failed to initialize Azure Blob Storage: {str(e)}")
    
    async def upload_file(self, file_path: str, remote_path: str) -> Dict[str, Any]:
        """
        Upload file to Azure Blob Storage | 上传文件到Azure Blob存储
        """
        try:
            # Upload file | 上传文件
            with open(file_path, "rb") as data:
                blob_client = self.client.get_blob_client(
                    container=self.container_name, 
                    blob=remote_path
                )
                blob_client.upload_blob(data, overwrite=True)
            
            return {
                "success": True,
                "url": self.get_file_url(remote_path),
                "message": f"File uploaded to Azure Blob Storage: {remote_path}"
            }
                
        except Exception as e:
            return {
                "success": False,
                "url": None,
                "message": f"Azure Blob Storage error: {str(e)}"
            }
    
    def get_file_url(self, remote_path: str) -> str:
        """
        Get Azure Blob Storage file URL | 获取Azure Blob存储文件URL
        """
        return f"{self.url_prefix.rstrip('/')}/{remote_path}"


class GoogleCloudStorageProvider(StorageProvider):
    """
    Google Cloud Storage provider | Google Cloud存储提供者
    """
    
    def __init__(self):
        try:
            from google.cloud import storage
            import json
            import os
            
            # Initialize client with credentials | 使用凭据初始化客户端
            if Config.GCS_CREDENTIALS_JSON:
                # If credentials are provided as JSON string | 如果凭据以JSON字符串形式提供
                try:
                    credentials_dict = json.loads(Config.GCS_CREDENTIALS_JSON)
                    # Write to temporary file for client initialization | 写入临时文件用于客户端初始化
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                        json.dump(credentials_dict, f)
                        credentials_file = f.name
                    
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
                    self.client = storage.Client()
                    # Clean up temporary file | 清理临时文件
                    os.unlink(credentials_file)
                    if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
                        del os.environ['GOOGLE_APPLICATION_CREDENTIALS']
                        
                except json.JSONDecodeError:
                    raise Exception("Invalid GCS credentials JSON format")
                    
            elif Config.GCS_CREDENTIALS_FILE:
                # If credentials file path is provided | 如果提供凭据文件路径
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.GCS_CREDENTIALS_FILE
                self.client = storage.Client()
                
            else:
                # Use default credentials (e.g., from environment) | 使用默认凭据（例如来自环境）
                self.client = storage.Client(project=Config.GCS_PROJECT_ID)
            
            self.bucket_name = Config.GCS_BUCKET_NAME
            self.url_prefix = Config.GCS_URL_PREFIX
            
            # Get bucket reference | 获取存储桶引用
            self.bucket = self.client.bucket(self.bucket_name)
            
            # Check if bucket exists | 检查存储桶是否存在
            if not self.bucket.exists():
                raise Exception(f"GCS bucket '{self.bucket_name}' does not exist")
            
        except ImportError:
            raise ImportError("Please install google-cloud-storage: pip install google-cloud-storage")
        except Exception as e:
            raise Exception(f"Failed to initialize Google Cloud Storage: {str(e)}")
    
    async def upload_file(self, file_path: str, remote_path: str) -> Dict[str, Any]:
        """
        Upload file to Google Cloud Storage | 上传文件到Google Cloud存储
        """
        try:
            # Create blob and upload file | 创建blob并上传文件
            blob = self.bucket.blob(remote_path)
            
            with open(file_path, "rb") as file_data:
                blob.upload_from_file(file_data)
            
            # Make blob publicly accessible if needed | 如果需要，使blob公开可访问
            # Note: This requires appropriate IAM permissions | 注意：这需要适当的IAM权限
            try:
                blob.make_public()
            except Exception:
                # If making public fails, continue anyway | 如果公开失败，继续执行
                pass
            
            return {
                "success": True,
                "url": self.get_file_url(remote_path),
                "message": f"File uploaded to Google Cloud Storage: {remote_path}"
            }
                
        except Exception as e:
            return {
                "success": False,
                "url": None,
                "message": f"Google Cloud Storage error: {str(e)}"
            }
    
    def get_file_url(self, remote_path: str) -> str:
        """
        Get Google Cloud Storage file URL | 获取Google Cloud存储文件URL
        """
        return f"{self.url_prefix.rstrip('/')}/{remote_path}"


class StorageManager:
    """
    Storage Manager | 存储管理器
    
    Manages different storage providers and handles file uploads.
    管理不同的存储提供者并处理文件上传。
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.storage_type = Config.STORAGE_TYPE.lower()
        self.provider = self._create_provider()
    
    def _create_provider(self) -> StorageProvider:
        """
        Create storage provider based on configuration | 根据配置创建存储提供者
        """
        try:
            if self.storage_type == "local":
                return LocalStorageProvider(self.output_dir, Config.get_local_storage_url_prefix())
            elif self.storage_type == "aliyun_oss":
                return AliyunOSSProvider()
            elif self.storage_type == "huawei_oceanstor":
                return HuaweiOceanStorProvider()
            elif self.storage_type == "minio":
                return MinIOProvider()
            elif self.storage_type == "amazon_s3":
                return AmazonS3Provider()
            elif self.storage_type == "azure_blob":
                return AzureBlobProvider()
            elif self.storage_type == "google_cloud_storage" or self.storage_type == "gcs":
                return GoogleCloudStorageProvider()
            else:
                print(f"Warning: Unknown storage type '{self.storage_type}', falling back to local storage")
                return LocalStorageProvider(self.output_dir, Config.get_local_storage_url_prefix())
        except Exception as e:
            print(f"Error initializing {self.storage_type} storage provider: {str(e)}")
            print("Falling back to local storage")
            return LocalStorageProvider(self.output_dir, Config.get_local_storage_url_prefix())
    
    async def save_mind_map(self, file_path: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Save mind map file to configured storage | 保存思维导图文件到配置的存储
        
        Args:
            file_path: Local file path to upload
            filename: Optional custom filename (without extension)
            
        Returns:
            Dict containing success status, URL, and message
        """
        try:
            # Generate filename if not provided | 如果未提供文件名则生成
            if not filename:
                timestamp = int(time.time())
                filename = f"mindmap_{timestamp}"
            
            # Ensure .png extension | 确保.png扩展名
            if not filename.endswith('.png'):
                filename += '.png'
            
            # Generate remote path with date folder structure | 生成带日期文件夹结构的远程路径
            from datetime import datetime
            date_folder = datetime.now().strftime("%Y/%m/%d")
            remote_path = f"{date_folder}/{filename}"
            
            # Upload file using provider | 使用提供者上传文件
            result = await self.provider.upload_file(file_path, remote_path)
            
            # Add storage type information | 添加存储类型信息
            result["storage_type"] = self.storage_type
            result["remote_path"] = remote_path
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "url": None,
                "message": f"Storage manager error: {str(e)}",
                "storage_type": self.storage_type
            }
    
    def get_storage_info(self) -> Dict[str, str]:
        """
        Get current storage configuration info | 获取当前存储配置信息
        """
        return {
            "storage_type": self.storage_type,
            "provider_class": self.provider.__class__.__name__,
            "description": self._get_storage_description()
        }
    
    def _get_storage_description(self) -> str:
        """
        Get storage type description | 获取存储类型描述
        """
        descriptions = {
            "local": "Local file system storage | 本地文件系统存储",
            "aliyun_oss": "Aliyun Object Storage Service | 阿里云对象存储服务",
            "huawei_oceanstor": "Huawei OceanStor Cloud Storage | 华为云对象存储服务",
            "minio": "MinIO Object Storage | MinIO对象存储",
            "amazon_s3": "Amazon S3 Cloud Storage | Amazon S3云存储",
            "azure_blob": "Azure Blob Storage | Azure Blob存储",
            "google_cloud_storage": "Google Cloud Storage | Google Cloud存储",
            "gcs": "Google Cloud Storage | Google Cloud存储"
        }
        return descriptions.get(self.storage_type, "Unknown storage type | 未知存储类型")
