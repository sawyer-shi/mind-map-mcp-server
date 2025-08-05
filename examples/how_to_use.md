# 如何使用思维导图MCP服务

## 什么是思维导图服务？

这个服务就像是一个智能画师，你给它文字描述，它就能画出漂亮的思维导图给你。

## 安装步骤

### 方法一：传统安装（需要一些技术基础）

1. **安装依赖软件**
   ```bash
   # 安装Node.js和Python
   # Windows用户可以从官网下载安装包
   # macOS用户可以使用Homebrew: brew install node python
   ```

2. **下载项目代码**
   ```bash
   git clone <项目地址>
   cd mind-map-mcp-server
   ```

3. **安装Python依赖**
   ```bash
   pip install -r requirements.txt
   python -m playwright install chromium
   ```

4. **安装Node.js依赖**
   ```bash
   npm install -g markmap-cli
   ```

5. **启动服务**
   ```bash
   python start_server.py
   ```

### 方法二：Docker安装（推荐，更简单）

1. **安装Docker**
   - Windows/Mac: 下载Docker Desktop
   - Linux: 使用包管理器安装docker

2. **启动服务**
   ```bash
   docker-compose up -d
   ```

就这么简单！服务会在 http://localhost:8090 启动。

## 如何使用

### 基本用法

1. **准备你的思维导图内容**
   用Markdown格式写出你的想法，例如：
   ```markdown
   # 我的项目计划
   ## 第一阶段
   - 需求分析
   - 技术选型
   ## 第二阶段
   - 开发实现
   - 测试优化
   ```

2. **发送请求**
   通过MCP客户端发送请求，服务会自动生成思维导图

3. **获得结果**
   系统会返回一张PNG格式的思维导图图片

### 在不同客户端中使用

#### Dify中使用
1. 在Dify中添加MCP服务
2. 配置服务地址: http://localhost:8090/mcp
3. 在聊天中直接使用思维导图功能

#### CherryStudio中使用
1. 添加MCP Server配置
2. 输入服务地址和端口
3. 开始使用思维导图工具

#### Claude Desktop中使用
1. 在配置文件中添加MCP服务器
2. 重启Claude Desktop
3. 使用思维导图工具

## 功能特点

### 支持的功能
✅ **自动生成思维导图**: 从Markdown文本生成可视化思维导图
✅ **中文字体支持**: 完美显示中文内容
✅ **高质量输出**: PNG格式，适合分享和打印
✅ **Docker部署**: 一键启动，环境隔离
✅ **REST API**: 支持HTTP接口调用

### 输入格式
- **Markdown格式**: 使用#表示标题层级
- **支持列表**: 使用-或*创建列表项
- **支持嵌套**: 多层级思维导图结构

### 输出格式
- **PNG图片**: 高清晰度，适合各种用途
- **自动布局**: 智能排版，美观大方
- **中文友好**: 完美支持中文字体显示

## 故障排除

### 常见问题

**Q: 服务启动失败？**
A: 检查端口8090是否被占用，可以修改docker-compose.yml中的端口配置

**Q: 生成的图片中文显示异常？**
A: 服务已内置中文字体支持，如仍有问题请检查Docker容器日志

**Q: 连接超时？**
A: 确认服务已启动，防火墙没有阻止8090端口

**Q: 图片质量不满意？**
A: 可以通过API参数调整图片尺寸和质量

### 获取帮助
- 查看日志: `docker-compose logs`
- 重启服务: `docker-compose restart`
- 完全重新部署: `docker-compose down && docker-compose up --build -d`

## 高级用法

### 自定义配置
可以通过环境变量自定义服务配置：
```bash
# 自定义端口
HOST_PORT=8080 docker-compose up -d

# 开启调试模式
DEBUG=true docker-compose up -d
```

### API接口
服务提供REST API接口，可以直接调用：
```bash
curl -X POST http://localhost:8090/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "create_mind_map", "params": {"content": "# 我的想法\n## 子想法"}}'
```

## 技术说明

### 架构设计
- **前端**: 无需前端，纯API服务
- **后端**: Python FastAPI框架
- **图像生成**: Playwright + Markmap
- **容器化**: Docker + Docker Compose

### 依赖组件
- **Python 3.11**: 主要运行环境
- **FastAPI**: Web框架
- **Playwright**: 浏览器自动化
- **Markmap**: 思维导图库
- **Node.js**: Markmap运行环境

这个服务让思维导图的创建变得简单而高效，希望对你的工作和学习有所帮助！