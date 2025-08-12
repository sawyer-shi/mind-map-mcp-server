# Google Cloud Storage Configuration Example | Google Cloud存储配置示例

This example shows how to configure Google Cloud Storage for the Mind Map MCP Server.
此示例展示如何为思维导图MCP服务器配置Google Cloud存储。

## Prerequisites | 前提条件

1. **Google Cloud Project** | Google Cloud项目
   - Create a Google Cloud project | 创建Google Cloud项目
   - Enable the Cloud Storage API | 启用Cloud Storage API

2. **Storage Bucket** | 存储桶
   - Create a Cloud Storage bucket | 创建Cloud Storage存储桶
   - Set appropriate permissions | 设置适当的权限

3. **Service Account** | 服务账户
   - Create a service account | 创建服务账户
   - Grant Storage Object Admin role | 授予存储对象管理员角色
   - Download the service account key JSON file | 下载服务账户密钥JSON文件

## Configuration Methods | 配置方法

### Method 1: Using Service Account Key File | 方法1：使用服务账户密钥文件

```bash
# .env file configuration | .env文件配置
STORAGE_TYPE=google_cloud_storage
GCS_PROJECT_ID=my-project-id
GCS_BUCKET_NAME=my-mindmap-bucket
GCS_CREDENTIALS_FILE=./credentials/service-account-key.json
GCS_URL_PREFIX=https://storage.googleapis.com/my-mindmap-bucket
```

### Method 2: Using Service Account Key JSON String | 方法2：使用服务账户密钥JSON字符串

```bash
# .env file configuration | .env文件配置
STORAGE_TYPE=google_cloud_storage
GCS_PROJECT_ID=my-project-id
GCS_BUCKET_NAME=my-mindmap-bucket
GCS_CREDENTIALS_JSON={"type":"service_account","project_id":"my-project-id","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"my-service@my-project.iam.gserviceaccount.com","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/my-service%40my-project.iam.gserviceaccount.com"}
GCS_URL_PREFIX=https://storage.googleapis.com/my-mindmap-bucket
```

### Method 3: Using Default Application Credentials | 方法3：使用默认应用凭据

```bash
# .env file configuration | .env文件配置
STORAGE_TYPE=google_cloud_storage
GCS_PROJECT_ID=my-project-id
GCS_BUCKET_NAME=my-mindmap-bucket
GCS_URL_PREFIX=https://storage.googleapis.com/my-mindmap-bucket

# Set environment variable before running | 运行前设置环境变量
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

## Installation | 安装

Install the Google Cloud Storage client library:
安装Google Cloud Storage客户端库：

```bash
pip install google-cloud-storage>=2.10.0
```

## Bucket Permissions | 存储桶权限

Ensure your service account has the following permissions:
确保您的服务账户具有以下权限：

- `storage.objects.create` - To upload files | 上传文件
- `storage.objects.get` - To read files | 读取文件
- `storage.objects.list` - To list files | 列出文件
- `storage.objects.delete` - To delete files (optional) | 删除文件（可选）

## Public Access Configuration | 公开访问配置

To make uploaded mind maps publicly accessible:
要使上传的思维导图公开可访问：

1. **Bucket-level public access** | 存储桶级公开访问
   ```bash
   # Make bucket publicly readable | 使存储桶公开可读
   gsutil iam ch allUsers:objectViewer gs://my-mindmap-bucket
   ```

2. **Individual object public access** | 单个对象公开访问
   - The storage provider will attempt to make each uploaded file public
   - 存储提供者将尝试使每个上传的文件公开

## File Organization | 文件组织

Mind map files are automatically organized by date:
思维导图文件按日期自动组织：

```
my-mindmap-bucket/
├── 2024/
│   ├── 01/
│   │   ├── 15/
│   │   │   ├── mindmap_1705123456.png
│   │   │   └── project_plan_1705234567.png
│   │   └── 16/
│   │       └── meeting_notes_1705345678.png
│   └── 02/
│       └── 01/
│           └── quarterly_review_1706456789.png
```

## Testing Configuration | 测试配置

To test your Google Cloud Storage configuration:
要测试您的Google Cloud Storage配置：

1. **Start the server** | 启动服务器
   ```bash
   python main.py
   ```

2. **Create a test mind map** | 创建测试思维导图
   ```bash
   # Use your MCP client to call create_mind_map
   # 使用您的MCP客户端调用create_mind_map
   ```

3. **Check the response** | 检查响应
   - Look for the GCS URL in the response | 在响应中查找GCS URL
   - Verify the file exists in your bucket | 验证文件是否存在于您的存储桶中

## Troubleshooting | 故障排除

### Common Issues | 常见问题

1. **Authentication Error** | 认证错误
   - Verify service account key is valid | 验证服务账户密钥是否有效
   - Check file path for credentials file | 检查凭据文件的文件路径

2. **Permission Denied** | 权限被拒绝
   - Ensure service account has Storage Object Admin role | 确保服务账户具有存储对象管理员角色
   - Check bucket permissions | 检查存储桶权限

3. **Bucket Not Found** | 存储桶未找到
   - Verify bucket name is correct | 验证存储桶名称是否正确
   - Ensure bucket exists in the specified project | 确保存储桶存在于指定的项目中

4. **Public Access Issues** | 公开访问问题
   - Check bucket public access settings | 检查存储桶公开访问设置
   - Verify object-level permissions | 验证对象级权限

### Debug Information | 调试信息

Enable debug logging to see detailed information:
启用调试日志以查看详细信息：

```bash
# .env file | .env文件
DEBUG=true
LOG_LEVEL=DEBUG
```

## Security Considerations | 安全考虑

1. **Service Account Key Security** | 服务账户密钥安全
   - Never commit service account keys to version control | 切勿将服务账户密钥提交到版本控制
   - Use environment variables or secure key management | 使用环境变量或安全密钥管理
   - Rotate keys regularly | 定期轮换密钥

2. **Bucket Access Control** | 存储桶访问控制
   - Use least privilege principle | 使用最小权限原则
   - Consider using signed URLs for private access | 考虑使用签名URL进行私有访问
   - Monitor access logs | 监控访问日志

3. **Cost Management** | 成本管理
   - Set up billing alerts | 设置计费警报
   - Use lifecycle policies for automatic cleanup | 使用生命周期策略进行自动清理
   - Monitor storage usage | 监控存储使用情况

## Example Output | 示例输出

When successfully configured, you'll see output like:
成功配置后，您将看到如下输出：

```json
{
  "success": true,
  "storage_url": "https://storage.googleapis.com/my-mindmap-bucket/2024/01/15/my_mindmap_1705123456.png",
  "storage_type": "google_cloud_storage",
  "storage_message": "File uploaded to Google Cloud Storage: 2024/01/15/my_mindmap_1705123456.png"
}
```
