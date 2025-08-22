# 🚀 一键部署思维导图生成器：Mind Map MCP Server 完整部署指南

> **🎯 让Markdown秒变精美思维导图！支持多云存储、无水印输出、Docker一键部署**

![Mind Map MCP Server](https://github.com/user-attachments/assets/b3f627b3-8720-4081-a047-909d01381d0b)

## 📖 项目简介

在这个信息爆炸的时代，如何将复杂的想法和知识结构化地表达出来？思维导图无疑是最佳选择之一。今天为大家介绍一个强大的开源项目：**Mind Map MCP Server** —— 一个能将Markdown文本瞬间转换为精美思维导图PNG图片的服务器。

### 🌟 为什么选择这个项目？

- **🚀 零门槛使用**：支持Docker一键部署，3分钟即可上线
- **🖼️ 高质量输出**：生成无水印的高清PNG图片
- **☁️ 多云存储**：支持本地、阿里云OSS、AWS S3等7种存储方式
- **🧠 智能适配**：自动分析内容复杂度，调整最佳视口尺寸
- **🌐 多语言支持**：完美支持中文、日文、阿拉伯语等Unicode字符
- **⚡ 高性能**：基于MCP协议，响应迅速

## 🎯 核心功能展示

### 功能1：Markdown转思维导图

**输入示例**：
```markdown
# 我的学习计划

## 编程学习
### 前端开发
- HTML基础
- CSS样式
- JavaScript

### 后端开发
- Python
- 数据库

## 项目实践
### 个人项目
- 个人博客
- 待办事项应用
```

**输出效果**：
![学习计划思维导图](https://github.com/user-attachments/assets/8e21ba12-26d5-4f69-bc22-5d5e876de4c6)

### 功能2：智能图片管理

- **按日期组织**：自动按YYYY/MM/DD结构保存
- **模糊搜索**：支持按名称过滤查找图片
- **直接访问**：每张图片都有独立的可分享URL

## 🛠️ 技术架构

### 🔧 技术栈
- **后端**：Python + FastAPI + MCP协议
- **前端渲染**：Playwright + markmap-cli
- **容器化**：Docker + Docker Compose
- **存储**：多云存储支持

### 📐 工作流程
```mermaid
graph LR
    A[Markdown输入] --> B[内容解析]
    B --> C[HTML生成]
    C --> D[浏览器渲染]
    D --> E[PNG输出]
    E --> F[云存储上传]
    F --> G[返回访问URL]
```

## 🚀 部署指南

### 方式一：Docker部署（🔥强烈推荐）

这是最简单、最可靠的部署方式，适合生产环境使用。

#### 1. 获取项目代码
```bash
git clone https://github.com/sawyer-shi/mind-map-mcp-server.git
cd mind-map-mcp-server
```

#### 2. 配置环境变量
```bash
# 复制配置模板
cp env.template .env

# 编辑配置文件
nano .env
```

**⚠️ 关键配置**：
```bash
# 必须修改：将127.0.0.1改为你的服务器IP
LOCAL_HOST=YOUR_SERVER_IP

# 端口配置（可选）
STREAMABLE_PORT=8091  # 主服务端口
STATIC_FILE_PORT=8090 # 静态文件端口

# 图片质量设置
IMAGE_QUALITY=high    # low/medium/high/ultra
```

#### 3. 一键启动服务
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose logs -f
```

#### 4. 验证部署成功
```bash
# 检查服务状态
curl http://YOUR_SERVER_IP:8091/health

# 访问主服务
curl http://YOUR_SERVER_IP:8091/
```

**🎉 部署成功！** 现在你可以通过以下地址访问：
- **MCP服务**：`http://YOUR_SERVER_IP:8091/mcp`
- **服务状态**：`http://YOUR_SERVER_IP:8091`
- **图片访问**：`http://YOUR_SERVER_IP:8090/output`

### 方式二：uvx部署（推荐开发环境）

适合Python开发者和需要频繁调试的场景。

#### 1. 安装uvx
```bash
# 使用pip安装
pip install uvx

# 或使用pipx安装
pipx install uvx
```

#### 2. 运行服务
```bash
# 进入项目目录
cd mind-map-mcp-server

# 启动HTTP模式
uvx --from . python main.py streamable-http --host 0.0.0.0 --port 8091

# 或启动stdio模式（用于MCP客户端集成）
uvx --from . python main.py stdio
```

### 方式三：传统安装

适合需要完全控制的高级用户。

#### 1. 安装依赖
```bash
# Python依赖
pip install -r requirements.txt

# Node.js依赖
npm install -g @markmap/cli

# 浏览器引擎
playwright install chromium
```

#### 2. 启动服务
```bash
# 自动安装并启动
python start_server.py

# 或手动启动
python main.py streamable-http
```

## ☁️ 多云存储配置

### 本地存储（默认）
```bash
STORAGE_TYPE=local
LOCAL_STORAGE_URL_PREFIX=http://YOUR_SERVER_IP:8090/output
```

### 阿里云OSS
```bash
STORAGE_TYPE=aliyun_oss
ALIYUN_OSS_ACCESS_KEY_ID=your_access_key_id
ALIYUN_OSS_ACCESS_KEY_SECRET=your_access_key_secret
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ALIYUN_OSS_BUCKET_NAME=your_bucket_name
ALIYUN_OSS_URL_PREFIX=https://your_bucket_name.oss-cn-hangzhou.aliyuncs.com
```

### Amazon S3
```bash
STORAGE_TYPE=amazon_s3
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=us-east-1
AWS_S3_BUCKET_NAME=your_bucket_name
AWS_S3_URL_PREFIX=https://your_bucket_name.s3.amazonaws.com
```

### Google Cloud Storage
```bash
STORAGE_TYPE=google_cloud_storage
GCS_PROJECT_ID=your_project_id
GCS_BUCKET_NAME=your_bucket_name
GCS_CREDENTIALS_FILE=path/to/service-account-key.json
GCS_URL_PREFIX=https://storage.googleapis.com/your_bucket_name
```

## 🎨 使用示例

### API调用示例

#### 创建思维导图
```bash
curl -X POST http://YOUR_SERVER_IP:8091/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_mind_map",
    "arguments": {
      "markdown_content": "# 项目规划\n\n## 开发阶段\n### 需求分析\n- 用户调研\n- 功能定义\n\n### 技术实现\n- 架构设计\n- 编码开发",
      "title": "项目规划图",
      "quality": "high"
    }
  }'
```

#### 查询图片列表
```bash
curl -X POST http://YOUR_SERVER_IP:8091/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "name": "list_images",
    "arguments": {
      "date": "2024-01-22",
      "name_filter": "项目"
    }
  }'
```

### 质量级别对比

| 级别 | 视口尺寸 | 缩放因子 | 适用场景 |
|------|----------|----------|----------|
| **low** | 800x600 | 1x | 快速预览 |
| **medium** | 1000x700 | 1.5x | 日常使用 |
| **high** | 1200x800 | 2x | 推荐默认 |
| **ultra** | 2400x1600 | 3x | 高质量输出 |

## 🔧 进阶配置

### Docker Compose服务说明

项目包含3个Docker服务：

1. **mind-map-streamable**：主MCP HTTP服务
2. **mind-map-static**：静态文件服务器
3. **mind-map-stdio**：命令行交互模式（可选）

### 端口配置详解

```bash
# 主服务端口
STREAMABLE_PORT=8091    # MCP HTTP服务

# 静态文件端口  
STATIC_FILE_PORT=8090   # 图片访问服务

# 内部端口（Docker）
FASTMCP_INTERNAL_PORT=8000  # 容器内部端口
```

### 性能优化建议

1. **内存配置**：
```yaml
# docker-compose.yml
services:
  mind-map-streamable:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

2. **并发设置**：
```bash
UVICORN_WORKERS=4        # 工作进程数
UVICORN_TIMEOUT=60       # 请求超时时间
```

## 🛠️ 常见问题解决

### Q: 图片显示为损坏链接？
**A**: 检查`LOCAL_HOST`配置是否正确
```bash
# ❌ 错误配置
LOCAL_HOST=127.0.0.1

# ✅ 正确配置  
LOCAL_HOST=YOUR_SERVER_IP
```

### Q: 思维导图只显示一个点？
**A**: 检查API参数名称
```json
{
  "name": "create_mind_map",
  "arguments": {
    "markdown_content": "# 正确的参数名",
    "title": "标题"
  }
}
```

### Q: 中文字符显示乱码？
**A**: 重新构建Docker镜像
```bash
docker-compose up --build -d
```

### Q: 服务启动失败？
**A**: 检查端口占用
```bash
# 检查端口占用
netstat -tulpn | grep :8091

# 修改端口配置
STREAMABLE_PORT=8092
```

## 📊 性能测试

### 基准测试结果

- **响应时间**：平均 < 2秒
- **并发处理**：支持50+并发请求
- **内存占用**：约200-500MB
- **支持格式**：Markdown → PNG
- **最大文件**：支持复杂层级结构

### 压力测试

```bash
# 使用ab进行压力测试
ab -n 100 -c 10 http://YOUR_SERVER_IP:8091/health

# 结果示例
Requests per second: 45.23 [#/sec]
Time per request: 221.1 [ms]
```

## 🔐 安全建议

### 1. 网络安全
```bash
# 使用防火墙限制访问
ufw allow from YOUR_IP_RANGE to any port 8091
ufw allow from YOUR_IP_RANGE to any port 8090
```

### 2. HTTPS配置
```nginx
# Nginx反向代理配置
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8091;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 访问控制
```bash
# 设置API密钥（可选）
API_KEY=your_secret_key

# 限制上传大小
MAX_CONTENT_SIZE=10MB
```

## 🚀 生产环境部署

### 1. 系统要求
- **操作系统**：Ubuntu 20.04+ / CentOS 8+ / Docker支持的任何系统
- **内存**：最少2GB，推荐4GB+
- **存储**：至少10GB可用空间
- **网络**：稳定的互联网连接

### 2. 监控配置
```yaml
# docker-compose.yml 添加健康检查
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8091/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 3. 日志管理
```bash
# 查看服务日志
docker-compose logs -f mind-map-streamable

# 日志轮转配置
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 4. 备份策略
```bash
# 备份输出目录
tar -czf backup-$(date +%Y%m%d).tar.gz output/

# 备份配置文件
cp .env .env.backup
```

## 📈 扩展功能

### 1. 自定义主题
```javascript
// 可通过修改markmap配置自定义主题
const markmapConfig = {
  color: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
  duration: 500,
  maxWidth: 300
};
```

### 2. 批量处理
```bash
# 批量转换多个Markdown文件
for file in *.md; do
  curl -X POST http://YOUR_SERVER_IP:8091/mcp \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"create_mind_map\",\"arguments\":{\"markdown_content\":\"$(cat $file)\",\"title\":\"${file%.md}\"}}"
done
```

### 3. API集成示例

#### Python客户端
```python
import requests
import json

def create_mindmap(content, title="Mind Map"):
    url = "http://YOUR_SERVER_IP:8091/mcp"
    payload = {
        "name": "create_mind_map",
        "arguments": {
            "markdown_content": content,
            "title": title,
            "quality": "high"
        }
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# 使用示例
markdown_content = """
# 项目架构
## 前端
- React
- TypeScript
## 后端  
- Python
- FastAPI
"""

result = create_mindmap(markdown_content, "项目架构图")
print(f"思维导图URL: {result['mind_map_image_url']}")
```

#### JavaScript客户端
```javascript
async function createMindMap(content, title = 'Mind Map') {
  const response = await fetch('http://YOUR_SERVER_IP:8091/mcp', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: 'create_mind_map',
      arguments: {
        markdown_content: content,
        title: title,
        quality: 'high'
      }
    })
  });
  
  return await response.json();
}

// 使用示例
const result = await createMindMap(`
# 学习计划
## 技术栈
### 前端
- Vue.js
- React
### 后端
- Node.js
- Python
`);

console.log('思维导图URL:', result.mind_map_image_url);
```

## 🎯 总结

Mind Map MCP Server 是一个功能强大、易于部署的思维导图生成服务。通过本指南，你可以：

✅ **快速部署**：3分钟Docker一键部署
✅ **灵活配置**：支持多种存储和质量选项  
✅ **生产就绪**：完整的监控、日志和安全配置
✅ **易于集成**：标准API接口，支持多语言客户端
✅ **高性能**：智能缓存和并发处理

### 🔗 相关链接

- **GitHub仓库**：https://github.com/sawyer-shi/mind-map-mcp-server
- **在线演示**：[即将上线]
- **技术文档**：项目中的ARCHITECTURE.md
- **示例代码**：examples/ 目录

### 💬 社区支持

如果你在部署过程中遇到问题，欢迎：

- 提交GitHub Issue
- 参与项目讨论
- 贡献代码和文档

---

**🎉 现在就开始你的思维导图之旅吧！** 

将复杂的想法转化为清晰的视觉图表，让知识管理变得更加高效和有趣。无论是个人学习、团队协作还是项目规划，Mind Map MCP Server 都是你的得力助手！

*最后更新：2024年1月*
