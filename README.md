# Mind Map MCP Server | 思维导图MCP服务器

[English](#english) | [中文](#chinese)

---

<a id="english"></a>

## 🌟 Mind Map MCP Server

A powerful MCP (Model Context Protocol) server that converts Markdown text into beautiful mind map PNG images.

### 👨‍💻 Author
**sawyer-shi**

### 📦 Repository
**Source Code**: https://github.com/sawyer-shi/mind-map-mcp-server.git

### ✨ Features

- 📝 **Markdown Input Support** - Convert any Markdown text to mind maps
- 🖼️ **High-Quality PNG Output** - Generate crisp, clear mind map images  
- 🐳 **Docker Ready** - One-command deployment with Docker
- 🔌 **Full MCP Protocol** - Standard MCP compliance for seamless integration
- ⚡ **Fast Generation** - Quick conversion and processing
- 🌐 **Multiple Access Methods** - HTTP and stdio transport support

### 🎯 Core Functions

#### 1. `create_mind_map`
- **Purpose**: Generate mind map PNG from Markdown content
- **Parameters**:
  - `markdown_content` (string): Markdown formatted text
  - `title` (string, optional): Mind map title
- **Returns**: Base64 encoded PNG image data

#### 2. `save_mind_map`  
- **Purpose**: Save generated mind map to local file
- **Parameters**:
  - `markdown_content` (string): Markdown formatted text
  - `filename` (string, optional): Output filename
- **Returns**: File path of saved image

### 🚀 Quick Start

#### Method 1: Docker Deployment (Recommended)

1. **Start the service**:
```bash
docker-compose up -d
```

2. **Access URLs**:
   - HTTP MCP Endpoint: `http://localhost:8091/mcp`
   - Service Status: `http://localhost:8091`

3. **Check service status**:
```bash
docker-compose logs -f
```

4. **Stop service**:
```bash
docker-compose down
```

#### Method 2: Local Installation

1. **Auto-install and start**:
```bash
python start_server.py
```

2. **Manual installation**:
```bash
pip install -r requirements.txt
npm install -g markmap-cli
playwright install chromium
python mind_map_server.py
```

### 🔗 MCP Client Configuration

#### For HTTP Transport (Recommended):
```json
{
  "mcpServers": {
    "mind-map-server": {
      "url": "http://localhost:8091/mcp"
    }
  }
}
```

#### For Docker + Stdio Transport:
```json
{
  "mcpServers": {
    "mind-map-server": {
      "command": "docker",
      "args": [
        "exec", 
        "-i", 
        "mind-map-mcp-server", 
        "python", 
        "mind_map_server.py"
      ]
    }
  }
}
```

### 📍 Configuration File Locations

**Claude Desktop Config**:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 🔧 Technical Architecture

1. **Markdown Parsing** - Process user input text
2. **HTML Conversion** - Use markmap-cli to create interactive HTML mind maps
3. **PNG Generation** - Use Playwright to capture HTML as PNG images
4. **MCP Protocol** - Standard MCP server implementation

### 📁 Project Structure
```
mind-map-mcp-server/
├── README.md                 # 📖 Project documentation
├── mind_map_server.py        # 🧠 Main MCP server (supports stdio & streamable-http)
├── start_server.py          # ⚙️ Auto-install startup script
├── start_streamable.py      # 🌐 Streamable HTTP startup script
├── quick_start.py           # 🚀 User-friendly startup interface
├── requirements.txt         # 🐍 Python dependencies
├── package.json            # 📦 Node.js dependencies  
├── Dockerfile              # 🐳 Docker build file
├── docker-compose.yml      # 🚢 Docker orchestration
├── env.template            # ⚙️ Environment configuration template
├── temp/                   # 📂 Temporary files
├── output/                 # 🖼️ Generated images
├── logs/                   # 📝 Log files
└── examples/               # 📋 Usage examples
```

### 🎬 Usage Example

**Input (Markdown)**:
```markdown
# My Learning Plan

## Programming
### Frontend
- HTML Basics
- CSS Styling  
- JavaScript

### Backend
- Python
- Databases

## Projects
### Personal Projects
- Personal Blog
- Todo App
```

**Output**: Beautiful PNG mind map visualizing the complete learning structure!

### ❓ FAQ

**Q: Can non-programmers use this?**
A: Absolutely! Just run `python start_server.py` and follow the prompts.

**Q: Why PNG instead of HTML?**
A: PNG images can be easily inserted into documents, presentations, and shared anywhere.

**Q: Docker vs local installation?**
A: Docker is simpler - just one command to start. Recommended for beginners.

**Q: Does it support non-English languages?**
A: Yes! Full Unicode support including Chinese, Japanese, Arabic, etc.

### 🛠️ Troubleshooting Guide

#### Common Issues and Solutions

**1. "Unexpected content type" Error**
- **Cause**: MCP client expects JSON responses for all requests
- **Solution**: Fixed in v1.0.1 - all responses now return proper JSON format
- **Status**: ✅ Resolved

**2. Chinese Characters Display as Garbled Text**
- **Cause**: Missing Chinese font support in Docker image
- **Solution**: Added Chinese fonts (Noto Sans CJK, WenQuanYi) and font injection to HTML
- **Status**: ✅ Resolved

**3. Mind Map Shows Only One Dot**
- **Cause**: Incorrect parameter name in API call
- **Correct Usage**: Use `markdown_content` (not `content`) as parameter name
- **Example**:
  ```json
  {
    "name": "create_mind_map",
    "arguments": {
      "markdown_content": "# Your Content Here",
      "title": "Optional Title"
    }
  }
  ```
- **Status**: ✅ Resolved

### 📋 Version History

- **v1.0.1**: Bug Fixes & Improvements
  - 🐛 Fixed "Unexpected content type" error
  - 🈶 Added Chinese font support for proper rendering
  - 📚 Enhanced documentation with troubleshooting guide
  - ✅ All known issues resolved

- **v1.0.0**: Initial Release
  - ✅ Markdown to PNG conversion
  - ✅ Complete MCP protocol implementation  
  - ✅ Docker one-click deployment
  - ✅ Auto-installation scripts
  - ✅ Multi-language support
  - ✅ HTTP + Stdio transports

---

<a id="chinese"></a>

## 🌟 思维导图MCP服务器

一个强大的MCP（模型上下文协议）服务器，可将Markdown文本转换为美观的思维导图PNG图片。

### 👨‍💻 作者
**sawyer-shi**

### 📦 代码仓库
**源码地址**: https://github.com/sawyer-shi/mind-map-mcp-server.git

### ✨ 功能特性

- 📝 **Markdown输入支持** - 将任何Markdown文本转换为思维导图
- 🖼️ **高质量PNG输出** - 生成清晰、美观的思维导图图片
- 🐳 **Docker就绪** - 一键Docker部署
- 🔌 **完整MCP协议** - 标准MCP合规，无缝集成
- ⚡ **快速生成** - 快速转换和处理
- 🌐 **多种访问方式** - 支持HTTP和stdio传输

### 🎯 核心功能

#### 1. `create_mind_map`
- **用途**：根据Markdown内容生成思维导图PNG
- **参数**：
  - `markdown_content` (字符串): Markdown格式的文本
  - `title` (字符串，可选): 思维导图标题
- **返回**：Base64编码的PNG图片数据

#### 2. `save_mind_map`
- **用途**：将生成的思维导图保存到本地文件
- **参数**：
  - `markdown_content` (字符串): Markdown格式的文本
  - `filename` (字符串，可选): 输出文件名
- **返回**：保存图片的文件路径

### 🚀 快速开始

#### 方式1：Docker部署（推荐）

1. **启动服务**：
```bash
docker-compose up -d
```

2. **访问地址**：
   - HTTP MCP端点：`http://localhost:8091/mcp`
   - 服务状态：`http://localhost:8091`

3. **查看服务状态**：
```bash
docker-compose logs -f
```

4. **停止服务**：
```bash
docker-compose down
```

#### 方式2：本地安装

1. **自动安装启动**：
```bash
python start_server.py
```

2. **手动安装**：
```bash
pip install -r requirements.txt
npm install -g markmap-cli
playwright install chromium
python mind_map_server.py
```

### 🔗 MCP客户端配置

#### HTTP传输方式（推荐）：
```json
{
  "mcpServers": {
    "mind-map-server": {
      "url": "http://localhost:8091/mcp"
    }
  }
}
```

#### Docker + Stdio传输方式：
```json
{
  "mcpServers": {
    "mind-map-server": {
      "command": "docker",
      "args": [
        "exec", 
        "-i", 
        "mind-map-mcp-server", 
        "python", 
        "mind_map_server.py"
      ]
    }
  }
}
```

### 📍 配置文件位置

**Claude Desktop配置**：
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 🔧 技术架构

1. **Markdown解析** - 处理用户输入文本
2. **HTML转换** - 使用markmap-cli创建交互式HTML思维导图
3. **PNG生成** - 使用Playwright将HTML捕获为PNG图片
4. **MCP协议** - 标准MCP服务器实现

### 📁 项目结构
```
mind-map-mcp-server/
├── README.md                 # 📖 项目文档
├── mind_map_server.py        # 🧠 主MCP服务器（支持stdio和streamable-http）
├── start_server.py          # ⚙️ 自动安装启动脚本
├── start_streamable.py      # 🌐 流式HTTP启动脚本
├── quick_start.py           # 🚀 用户友好的启动界面
├── requirements.txt         # 🐍 Python依赖
├── package.json            # 📦 Node.js依赖  
├── Dockerfile              # 🐳 Docker构建文件
├── docker-compose.yml      # 🚢 Docker编排
├── env.template            # ⚙️ 环境配置模板
├── temp/                   # 📂 临时文件
├── output/                 # 🖼️ 生成的图片
├── logs/                   # 📝 日志文件
└── examples/               # 📋 使用示例
```

### 🎬 使用示例

**输入（Markdown）**：
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

**输出**：生成一张美观的PNG思维导图，展示完整的学习计划结构！

### ❓ 常见问题

**Q: 不懂编程的人能用吗？**
A: 当然可以！运行 `python start_server.py`，按照提示操作即可。

**Q: 为什么输出PNG而不是HTML？**
A: PNG图片可以轻松插入到文档、演示文稿中，方便在任何地方分享。

**Q: Docker还是本地安装？**
A: Docker更简单 - 只需一个命令即可启动，推荐初学者使用。

**Q: 支持中文吗？**
A: 完全支持！包括中文、日文、阿拉伯语等所有Unicode字符。

### 🛠️ 故障排除指南

#### 常见问题和解决方案

**1. "Unexpected content type" 错误**
- **原因**：MCP客户端期望所有请求都返回JSON响应
- **解决方案**：v1.0.1版本已修复 - 所有响应现在都返回正确的JSON格式
- **状态**：✅ 已解决

**2. 中文字符显示为乱码**
- **原因**：Docker镜像中缺少中文字体支持
- **解决方案**：添加了中文字体（Noto Sans CJK、文泉驿）并在HTML中注入字体
- **状态**：✅ 已解决

**3. 思维导图只显示一个点**
- **原因**：API调用中使用了错误的参数名
- **正确用法**：使用`markdown_content`（不是`content`）作为参数名
- **示例**：
  ```json
  {
    "name": "create_mind_map",
    "arguments": {
      "markdown_content": "# 你的内容",
      "title": "可选标题"
    }
  }
  ```
- **状态**：✅ 已解决

### 📋 版本历史

- **v1.0.1**: Bug修复和改进
  - 🐛 修复了"Unexpected content type"错误
  - 🈶 添加了中文字体支持以确保正确渲染
  - 📚 增强了文档，添加了故障排除指南
  - ✅ 所有已知问题已解决

- **v1.0.0**: 初始发布版本
  - ✅ Markdown到PNG转换
  - ✅ 完整的MCP协议实现  
  - ✅ Docker一键部署
  - ✅ 自动安装脚本
  - ✅ 多语言支持
  - ✅ HTTP + Stdio传输

## ⚠️ 注意事项 | Notes

- 🌐 需要网络连接（下载依赖时）| Network required for dependency downloads
- 💾 PNG图片保存在output目录 | PNG images saved in output directory
- 🧹 临时文件自动清理 | Temporary files auto-cleaned
- 🖥️ 支持Windows、Mac、Linux | Cross-platform support
- 🚪 默认端口：8091 | Default port: 8091

## 📄 License | 许可证

MIT License - see LICENSE for details.

---

**Created with ❤️ by sawyer-shi**