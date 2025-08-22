# 🚀 Mind Map MCP Server 部署指南

## 📋 部署方式选择

### 🔥 生产环境部署（推荐）

使用预构建的Docker Hub镜像，快速、稳定、易维护。

```bash
# 1. 配置环境
cp env.template .env
# 编辑 .env 文件，设置 LOCAL_HOST 为您的服务器IP

# 2. 启动服务
docker-compose up -d

# 3. 访问服务
# MCP服务: http://YOUR_SERVER_IP:8091/mcp
# 静态文件: http://YOUR_SERVER_IP:8090/output
```

**特点**：
- ✅ 使用 `sawyershi/mind-map-mcp-server:latest` 镜像
- ✅ 无需本地构建，启动速度快
- ✅ 适合生产环境和用户快速体验
- ✅ 镜像版本统一，便于维护

### 🔧 开发环境部署

使用本地源代码构建，适合开发和调试。

```bash
# 1. 配置环境
cp env.template .env
# 编辑 .env 文件进行自定义配置

# 2. 启动开发服务
docker-compose -f docker-compose.dev.yml up -d

# 3. 重新构建（代码更改后）
docker-compose -f docker-compose.dev.yml up --build -d
```

**特点**：
- ✅ 从本地源码构建 `mind-map-mcp-server:unified` 镜像
- ✅ 支持代码修改和实时调试
- ✅ 容器名带 `-dev` 后缀，避免冲突
- ✅ 适合开发者和贡献者

## 📊 配置对比

| 特性 | 生产环境 (`docker-compose.yml`) | 开发环境 (`docker-compose.dev.yml`) |
|------|--------------------------------|-------------------------------------|
| **镜像来源** | Docker Hub | 本地构建 |
| **镜像名称** | `sawyershi/mind-map-mcp-server:latest` | `mind-map-mcp-server:unified` |
| **容器名称** | `mind-map-*` | `mind-map-*-dev` |
| **启动速度** | 快（直接拉取） | 慢（需要构建） |
| **适用场景** | 生产部署、用户体验 | 开发调试、代码修改 |
| **网络要求** | 需要网络拉取镜像 | 需要网络下载依赖 |

## 🎯 服务说明

### 服务组件

1. **mind-map-streamable**: 主HTTP服务（端口8091）
2. **mind-map-static**: 静态文件服务（端口8090）
3. **mind-map-stdio**: 命令行交互模式（可选）

### 端口映射

- `8091`: MCP HTTP服务端点
- `8090`: 静态文件服务器
- `8000`: 容器内部FastMCP端口

## 🔧 常用命令

### 生产环境

```bash
# 启动所有服务
docker-compose up -d

# 启动包含stdio的所有服务
docker-compose --profile stdio up -d

# 查看日志
docker-compose logs -f mind-map-streamable

# 停止服务
docker-compose down
```

### 开发环境

```bash
# 启动开发服务
docker-compose -f docker-compose.dev.yml up -d

# 重新构建并启动
docker-compose -f docker-compose.dev.yml up --build -d

# 查看开发日志
docker-compose -f docker-compose.dev.yml logs -f mind-map-streamable

# 停止开发服务
docker-compose -f docker-compose.dev.yml down
```

## 🚨 重要提醒

### 生产部署必读

1. **修改LOCAL_HOST**：
   ```bash
   # ❌ 错误（只能本机访问）
   LOCAL_HOST=127.0.0.1
   
   # ✅ 正确（外部可访问）
   LOCAL_HOST=192.168.1.100  # 您的服务器IP
   ```

2. **端口冲突检查**：
   ```bash
   # 检查端口占用
   netstat -tulpn | grep :8091
   netstat -tulpn | grep :8090
   ```

3. **防火墙配置**：
   ```bash
   # Ubuntu/Debian
   ufw allow 8091
   ufw allow 8090
   ```

## 🔄 环境切换

### 从开发切换到生产

```bash
# 停止开发环境
docker-compose -f docker-compose.dev.yml down

# 启动生产环境
docker-compose up -d
```

### 从生产切换到开发

```bash
# 停止生产环境
docker-compose down

# 启动开发环境
docker-compose -f docker-compose.dev.yml up -d
```

## 📈 性能建议

### 生产环境优化

- 使用SSD存储提升I/O性能
- 配置足够内存（推荐4GB+）
- 启用Docker日志轮转
- 定期清理临时文件

### 开发环境优化

- 使用本地缓存加速构建
- 启用Docker BuildKit
- 配置合理的资源限制

## 🆘 故障排除

### 常见问题

1. **服务无法启动**：检查端口占用和权限
2. **图片无法访问**：检查LOCAL_HOST配置
3. **构建失败**：检查网络连接和磁盘空间
4. **中文乱码**：重新构建镜像或拉取最新版本

### 日志查看

```bash
# 生产环境
docker-compose logs -f

# 开发环境
docker-compose -f docker-compose.dev.yml logs -f
```

---

选择适合您需求的部署方式，开始您的思维导图之旅！🎉
