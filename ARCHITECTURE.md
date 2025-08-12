# Project Architecture | 项目架构

## Overview | 概述

This document describes the new modular architecture of the Mind Map MCP Server.
本文档描述了思维导图MCP服务器的新模块化架构。

## Directory Structure | 目录结构

```
mind-map-mcp-server/
├── main.py                    # New main entry point | 新的主入口点
├── mind_map_server.py         # Legacy entry point (deprecated) | 旧版入口点（已弃用）
├── src/                       # Source code modules | 源代码模块
│   ├── __init__.py           # Package initialization | 包初始化
│   ├── config.py             # Configuration management | 配置管理
│   ├── server.py             # Main server class | 主服务器类
│   ├── mind_map_generator.py # Mind map generation logic | 思维导图生成逻辑
│   ├── mcp_tools.py          # MCP tool definitions | MCP工具定义
│   └── utils.py              # Utility functions | 工具函数
├── start_server.py           # Auto-install startup script | 自动安装启动脚本
├── quick_start.py            # Interactive startup menu | 交互式启动菜单
├── examples/                 # Usage examples | 使用示例
├── temp/                     # Temporary files | 临时文件
├── output/                   # Generated images | 生成的图片
└── logs/                     # Log files | 日志文件
```

## Module Descriptions | 模块说明

### Core Modules | 核心模块

#### `main.py`
- **Purpose**: New unified entry point for both transport modes | 新的统一入口点，支持两种传输模式
- **Features**: Transport selection, auto-configuration | 传输选择，自动配置
- **Usage**: `python main.py [stdio|streamable-http]`

#### `src/server.py` 
- **Purpose**: Main MCP server implementation | 主MCP服务器实现
- **Features**: Transport abstraction, request handling | 传输抽象，请求处理
- **Architecture**: Modular design with pluggable transports | 模块化设计，可插拔传输

#### `src/mind_map_generator.py`
- **Purpose**: Core mind map generation logic | 核心思维导图生成逻辑  
- **Features**: Markdown parsing, HTML generation, PNG conversion | Markdown解析，HTML生成，PNG转换
- **Dependencies**: markmap-cli, playwright | 依赖markmap-cli，playwright

#### `src/mcp_tools.py`
- **Purpose**: MCP tool definitions and schemas | MCP工具定义和模式
- **Tools**: `create_mind_map`, `save_mind_map` | 工具：创建思维导图，保存思维导图
- **Validation**: Pydantic schemas for type safety | Pydantic模式确保类型安全

### Utility Modules | 工具模块

#### `src/config.py`
- **Purpose**: Configuration management and environment setup | 配置管理和环境设置
- **Features**: Environment variable loading, default values | 环境变量加载，默认值
- **Support**: .env file integration | 支持.env文件集成

#### `src/utils.py`
- **Purpose**: Shared utility functions | 共享工具函数
- **Functions**: File operations, logging, validation | 文件操作，日志记录，验证
- **Reusability**: Used across all modules | 可重用性：跨所有模块使用

### Legacy Support | 遗留支持

#### `mind_map_server.py`
- **Status**: Deprecated but maintained for compatibility | 已弃用但为兼容性而保留
- **Purpose**: Original monolithic server implementation | 原始单体服务器实现
- **Migration**: Users should migrate to `main.py` | 用户应迁移到main.py

## Transport Architecture | 传输架构

### Stdio Transport | Stdio传输
- **Protocol**: Standard input/output streams | 标准输入/输出流
- **Use Case**: Local tools, command-line clients | 本地工具，命令行客户端
- **Implementation**: Direct MCP protocol over stdin/stdout | 通过stdin/stdout直接实现MCP协议

### Streamable HTTP Transport | 流式HTTP传输
- **Protocol**: HTTP with streaming support | 支持流式的HTTP
- **Use Case**: Web applications, remote clients | Web应用程序，远程客户端
- **Implementation**: FastAPI + FastMCP integration | FastAPI + FastMCP集成
- **Port**: Default 8091 (configurable) | 默认端口8091（可配置）

## Data Flow | 数据流

```
Input (Markdown) → Parser → HTML Generator → Browser Renderer → PNG Output
输入(Markdown) → 解析器 → HTML生成器 → 浏览器渲染器 → PNG输出
```

### Detailed Steps | 详细步骤

1. **Input Processing | 输入处理**
   - Receive Markdown content via MCP | 通过MCP接收Markdown内容
   - Validate and sanitize input | 验证并清理输入

2. **HTML Generation | HTML生成**
   - Use markmap-cli to convert Markdown to HTML | 使用markmap-cli将Markdown转换为HTML
   - Apply custom styling and fonts | 应用自定义样式和字体

3. **PNG Conversion | PNG转换**
   - Launch headless browser with Playwright | 使用Playwright启动无头浏览器
   - Capture HTML as high-quality PNG | 将HTML捕获为高质量PNG

4. **Output Handling | 输出处理**
   - Return base64 encoded image or file path | 返回base64编码图像或文件路径
   - Clean up temporary files | 清理临时文件

## Configuration | 配置

### Environment Variables | 环境变量

- `HOST`: Server bind address | 服务器绑定地址 (default: 0.0.0.0)
- `STREAMABLE_PORT`: HTTP transport port | HTTP传输端口 (default: 8091)
- `DEBUG`: Enable debug mode | 启用调试模式 (default: false)
- `LOG_LEVEL`: Logging level | 日志级别 (default: INFO)

### File Configuration | 文件配置

- `.env`: Environment variable overrides | 环境变量覆盖
- `env.template`: Configuration template | 配置模板

## Docker Integration | Docker集成

### Multi-Transport Support | 多传输支持
- Single unified Docker image | 单一统一Docker镜像
- Runtime transport selection | 运行时传输选择
- Profile-based service management | 基于配置文件的服务管理

### Services | 服务
- `mind-map-stdio`: Stdio transport service | Stdio传输服务
- `mind-map-streamable`: HTTP transport service | HTTP传输服务

## Development Guidelines | 开发指南

### Code Organization | 代码组织
- Keep modules focused and single-purpose | 保持模块专注和单一目的
- Use type hints and Pydantic validation | 使用类型提示和Pydantic验证
- Follow consistent error handling patterns | 遵循一致的错误处理模式

### Testing | 测试
- Unit tests for individual modules | 单个模块的单元测试
- Integration tests for transport protocols | 传输协议的集成测试
- End-to-end tests for complete workflows | 完整工作流的端到端测试

### Documentation | 文档
- Inline comments for complex logic | 复杂逻辑的内联注释
- Docstrings for all public functions | 所有公共函数的文档字符串
- Architecture updates for major changes | 重大更改的架构更新

## Migration Guide | 迁移指南

### From Legacy Server | 从遗留服务器迁移

1. **Update Entry Point | 更新入口点**
   ```bash
   # Old | 旧版
   python mind_map_server.py
   
   # New | 新版
   python main.py stdio
   python main.py streamable-http
   ```

2. **Configuration Changes | 配置更改**
   - Move environment variables to .env file | 将环境变量移至.env文件
   - Update Docker commands to use new services | 更新Docker命令以使用新服务

3. **Client Integration | 客户端集成**
   - Stdio clients: No changes required | Stdio客户端：无需更改
   - HTTP clients: Update endpoint URLs | HTTP客户端：更新端点URL

## Future Enhancements | 未来增强

- **WebSocket Transport**: Real-time bidirectional communication | WebSocket传输：实时双向通信
- **Plugin System**: Extensible tool registration | 插件系统：可扩展工具注册
- **Caching Layer**: Improved performance for repeated requests | 缓存层：提高重复请求的性能
- **Multi-format Output**: SVG, PDF support | 多格式输出：SVG，PDF支持