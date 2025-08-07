"""
Mind Map MCP Server | 思维导图MCP服务器
==========================================================

This server supports two MCP transport protocols:
1. stdio - Standard input/output (best for local tools)
2. streamablehttp - Streamable HTTP (modern web standard)

本服务器支持两种MCP传输协议：
1. stdio - 标准输入/输出（适用于本地工具）
2. streamablehttp - 可流式HTTP（现代Web标准）

Simply put: you give it text, it gives you pictures!
简单来说：你给它文字，它给你图片！
"""

import argparse
import asyncio
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
from typing import Any, Sequence
from pathlib import Path

# Load environment variables from .env file if available | 如果可用，从.env文件加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, environment variables will be loaded from system
    # python-dotenv未安装，环境变量将从系统加载
    pass

# MCP related imports - tools that enable the service to work with MCP protocol
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
    from mcp.server.fastmcp import FastMCP  # For modern transport support
except ImportError:
    print("Please install MCP library: pip install 'mcp[cli]'")
    sys.exit(1)

# Browser automation tools - used to convert web pages to images
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Please install Playwright: pip install playwright")
    print("Then run: playwright install chromium")
    sys.exit(1)


# Configuration management | 配置管理
class Config:
    """Configuration management class | 配置管理类"""
    
    @staticmethod
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
    
    # Server configuration | 服务器配置
    HOST = get_env.__func__("HOST", "0.0.0.0")
    LOCAL_HOST = get_env.__func__("LOCAL_HOST", "127.0.0.1")
    
    # Port configuration | 端口配置
    STREAMABLE_PORT = get_env.__func__("STREAMABLE_PORT", "8091", int)
    FASTMCP_INTERNAL_PORT = get_env.__func__("FASTMCP_INTERNAL_PORT", "8000", int)
    
    # Debug configuration | 调试配置
    DEBUG = get_env.__func__("DEBUG", "false", bool)
    LOG_LEVEL = get_env.__func__("LOG_LEVEL", "INFO")
    
    # Directory configuration | 目录配置
    HOST_TEMP_PATH = get_env.__func__("HOST_TEMP_PATH", "./temp")
    HOST_OUTPUT_PATH = get_env.__func__("HOST_OUTPUT_PATH", "./output")
    HOST_LOG_PATH = get_env.__func__("HOST_LOG_PATH", "./logs")


class MindMapServer:
    """
    Mind Map Server Class | 思维导图服务器类
    
    Like a specialized mind map factory:
    - Has order receiving functionality (accepts Markdown text)
    - Has production workshop (converts text to mind maps)
    - Has quality control and packaging (generates PNG images)
    
    就像一个专业的思维导图工厂：
    - 有接单功能（接收Markdown文本）
    - 有生产车间（将文本转换为思维导图）
    - 有质检打包（生成PNG图片）
    """
    
    def __init__(self):
        # Create necessary directories | 创建必要目录
        self.temp_dir = Path("temp")
        self.output_dir = Path("output")
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize MCP server | 初始化MCP服务器
        self.server = Server("mind-map-server")
        
        # Register service functions - tell the world what we can do
        # 注册服务功能 - 告诉外界我们能做什么
        self._register_tools()
        
    def _register_tools(self):
        """
        Register tool functions | 注册工具函数
        
        Like posting a service menu at a service desk, letting customers know what services we provide
        就像在服务台张贴服务菜单，让客户知道我们提供什么服务
        """
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """Return list of all available tools"""
            return [
                Tool(
                    name="create_mind_map",
                    description="Generate mind map PNG image from Markdown content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "markdown_content": {
                                "type": "string", 
                                "description": "Markdown format text content"
                            },
                            "title": {
                                "type": "string", 
                                "description": "Mind map title (optional)",
                                "default": "Mind Map"
                            }
                        },
                        "required": ["markdown_content"]
                    }
                ),
                Tool(
                    name="save_mind_map",
                    description="Save mind map to file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "markdown_content": {
                                "type": "string",
                                "description": "Markdown format text content"
                            },
                            "filename": {
                                "type": "string",
                                "description": "Save filename (optional, auto-generated if not provided)"
                            }
                        },
                        "required": ["markdown_content"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> Sequence[TextContent | ImageContent]:
            """Handle tool calls"""
            if name == "create_mind_map":
                markdown_content = arguments.get("markdown_content", "")
                title = arguments.get("title", "Mind Map")
                return await self._create_mind_map(markdown_content, title)
            elif name == "save_mind_map":
                markdown_content = arguments.get("markdown_content", "")
                filename = arguments.get("filename")
                return await self._save_mind_map(markdown_content, filename)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

    async def _create_mind_map(self, markdown_content: str, title: str = "Mind Map") -> Sequence[TextContent | ImageContent]:
        """
        Generate mind map | 生成思维导图
        
        This function is responsible for converting your text into a beautiful mind map image
        这个函数负责将你的文字转换成漂亮的思维导图图片
        """
        try:
            print(f"Starting mind map generation: {title}")
            
            # Clean up old temporary files | 清理旧的临时文件
            self._cleanup_temp_files()
            
            # Generate unique filename | 生成唯一文件名
            timestamp = int(time.time())
            temp_md_file = self.temp_dir / f"mindmap_{timestamp}.md"
            temp_html_file = self.temp_dir / f"mindmap_{timestamp}.html"
            temp_png_file = self.temp_dir / f"mindmap_{timestamp}.png"
            
            # Write Markdown content to file | 将Markdown内容写入文件
            with open(temp_md_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print("Converting Markdown to HTML mind map...")
            
            # Use markmap-cli to convert Markdown to HTML | 使用markmap-cli将Markdown转换为HTML
            cmd = [
                'npx', 'markmap-cli', 
                str(temp_md_file), 
                '-o', str(temp_html_file),
                '--no-open'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                error_msg = f"Markmap conversion failed: {result.stderr}"
                print(f"Error: {error_msg}")
                return [TextContent(type="text", text=error_msg)]
            
            # Fix Chinese font support in generated HTML | 修复生成HTML中的中文字体支持
            self._fix_chinese_fonts(temp_html_file)
            
            print("Converting HTML to PNG...")
            
            # Use Playwright to convert HTML to PNG | 使用Playwright将HTML转换为PNG
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--no-first-run',
                        '--no-zygote',
                        '--disable-features=VizDisplayCompositor',
                        '--font-render-hinting=none',
                        '--disable-font-subpixel-positioning'
                    ]
                )
                page = await browser.new_page()
                
                # Set viewport size for better screenshot quality | 设置视口大小以获得更好的截图质量
                await page.set_viewport_size({"width": 1200, "height": 800})
                
                # Load HTML file | 加载HTML文件
                await page.goto(f"file://{temp_html_file.absolute()}")
                
                # Wait for page to fully load | 等待页面完全加载
                await page.wait_for_timeout(2000)
                
                # Take screenshot | 截图
                await page.screenshot(path=str(temp_png_file), full_page=True)
                
                await browser.close()
            
            # Read PNG file and encode as base64 | 读取PNG文件并编码为base64
            with open(temp_png_file, 'rb') as f:
                png_data = base64.b64encode(f.read()).decode('utf-8')
            
            print(f"Mind map generated successfully: {temp_png_file}")
            
            return [
                ImageContent(
                    type="image",
                    data=png_data,
                    mimeType="image/png"
                ),
                TextContent(
                    type="text", 
                    text=f"Mind map '{title}' generated successfully!"
                )
            ]
            
        except Exception as e:
            error_msg = f"Mind map generation failed: {str(e)}"
            print(f"Error: {error_msg}")
            return [TextContent(type="text", text=error_msg)]
    
    async def _save_mind_map(self, markdown_content: str, filename: str = None) -> Sequence[TextContent]:
        """
        Save mind map to file | 将思维导图保存到文件
        
        This function saves the generated image to your computer
        这个函数将生成的图片保存到你的电脑上
        """
        try:
            # If no filename specified, use timestamp as filename | 如果没有指定文件名，使用时间戳作为文件名
            if not filename:
                filename = f"mindmap_{int(time.time())}"
            
            # Ensure filename doesn't have extension | 确保文件名没有扩展名
            if filename.endswith('.png'):
                filename = filename[:-4]
            
            # Generate mind map | 生成思维导图
            result = await self._create_mind_map(markdown_content, filename)
            
            # Extract PNG data and save | 提取PNG数据并保存
            for item in result:
                if hasattr(item, 'data') and item.type == "image":
                    png_data = base64.b64decode(item.data)
                    output_file = self.output_dir / f"{filename}.png"
                    
                    with open(output_file, 'wb') as f:
                        f.write(png_data)
                    
                    return [TextContent(
                        type="text",
                        text=f"Mind map saved successfully to: {output_file}"
                    )]
            
            # If we get here, no image was generated | 如果执行到这里，说明没有生成图片
            return [TextContent(
                type="text",
                text="Failed to generate mind map image"
            )]
            
        except Exception as e:
            error_msg = f"Failed to save mind map: {str(e)}"
            print(f"Error: {error_msg}")
            return [TextContent(type="text", text=error_msg)]

    def _fix_chinese_fonts(self, html_file):
        """Fix Chinese font support and remove watermark in generated HTML | 修复生成HTML中的中文字体支持并去除水印"""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Replace the default font-family with Chinese-friendly fonts | 用中文友好字体替换默认字体
            old_font_css = "font-family: ui-sans-serif, system-ui, sans-serif, 'Apple Color Emoji',\n    'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';"
            new_font_css = "font-family: 'Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'WenQuanYi Micro Hei', 'Microsoft YaHei', 'SimHei', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';"
            
            html_content = html_content.replace(old_font_css, new_font_css)
            
            # Remove markmap watermark | 去除markmap水印
            # Hide the watermark by adding CSS to make it invisible | 通过添加CSS来隐藏水印
            additional_css = """
svg text {
  font-family: 'Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'WenQuanYi Micro Hei', 'Microsoft YaHei', 'SimHei', sans-serif !important;
  font-weight: normal;
}

/* Hide markmap watermark | 隐藏markmap水印 */
.mm-brand, .mm-brand-name, [data-testid="brand"], .markmap-brand, 
text[text-anchor="end"][font-size]:last-child,
svg text:last-child[text-anchor="end"],
svg g:last-child text[text-anchor="end"],
text[fill="currentColor"][text-anchor="end"]:last-of-type {
  display: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
}

/* Additional watermark hiding methods | 额外的水印隐藏方法 */
svg > g:last-child > text[text-anchor="end"] { display: none !important; }
svg text[dy="0.31em"][text-anchor="end"] { display: none !important; }
"""
            
            # Insert additional CSS before </style> | 在</style>之前插入额外的CSS
            html_content = html_content.replace('</style>', additional_css + '</style>')
            
            # Also try to remove watermark text directly from the HTML | 也尝试直接从HTML中删除水印文本
            import re
            # Remove markmap watermark text patterns | 删除markmap水印文本模式
            watermark_patterns = [
                r'<text[^>]*text-anchor="end"[^>]*>markmap</text>',
                r'<text[^>]*>markmap</text>',
                r'markmap</text>',
                r'<g[^>]*class="mm-brand"[^>]*>.*?</g>',
            ]
            
            for pattern in watermark_patterns:
                html_content = re.sub(pattern, '', html_content, flags=re.IGNORECASE | re.DOTALL)
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            print("Chinese font support added and watermark removed from HTML")
            
        except Exception as e:
            print(f"Warning: Failed to fix Chinese fonts and remove watermark: {e}")

    def _cleanup_temp_files(self):
        """Clean up old temporary files | 清理旧的临时文件"""
        try:
            # Clean files older than 1 hour | 清理1小时前的文件
            current_time = time.time()
            for file in self.temp_dir.glob("mindmap_*"):
                if current_time - file.stat().st_mtime > 3600:  # 1 hour
                    file.unlink()
                    print(f"Cleaned up temporary file: {file}")
        except Exception as e:
            print(f"Failed to clean up file {file}: {e}")
    
    async def run_stdio(self):
        """Start MCP server in stdio mode | 以stdio模式启动MCP服务器"""
        print("Starting Mind Map MCP Server - stdio mode...")
        print("Available functions:")
        print("   - create_mind_map: Generate mind map PNG")
        print("   - save_mind_map: Save mind map to file")
        print("Server ready, waiting for MCP requests...")
        
        # Run standard MCP server | 运行标准MCP服务器
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mind-map-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
    
    def create_fastmcp_server(self):
        """Create FastMCP server instance for modern transports | 创建FastMCP服务器实例用于现代传输"""
        mcp = FastMCP("Mind Map MCP Server")
        
        @mcp.tool()
        async def create_mind_map(markdown_content: str, title: str = "Mind Map") -> dict:
            """Generate mind map from Markdown content | 从Markdown内容生成思维导图"""
            try:
                print(f"Starting mind map generation: {title}")
                
                # Clean up old temporary files | 清理旧的临时文件
                self._cleanup_temp_files()
                
                # Generate unique filename | 生成唯一文件名
                timestamp = int(time.time())
                temp_md_file = self.temp_dir / f"mindmap_{timestamp}.md"
                temp_html_file = self.temp_dir / f"mindmap_{timestamp}.html"
                temp_png_file = self.temp_dir / f"mindmap_{timestamp}.png"
                
                # Write Markdown content to file | 将Markdown内容写入文件
                with open(temp_md_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                print("Converting Markdown to HTML mind map...")
                
                # Use markmap-cli to convert Markdown to HTML | 使用markmap-cli将Markdown转换为HTML
                cmd = [
                    'npx', 'markmap-cli', 
                    str(temp_md_file), 
                    '-o', str(temp_html_file),
                    '--no-open'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    error_msg = f"Markmap conversion failed: {result.stderr}"
                    print(f"Error: {error_msg}")
                    return {"error": error_msg, "success": False}
                
                # Fix Chinese font support and remove watermark | 修复中文字体支持并去除水印
                self._fix_chinese_fonts(temp_html_file)
                
                print("Converting HTML to PNG...")
                
                # Use Playwright to convert HTML to PNG | 使用Playwright将HTML转换为PNG
                async with async_playwright() as p:
                    browser = await p.chromium.launch(
                        headless=True,
                        args=[
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-gpu',
                            '--no-first-run',
                            '--no-zygote',
                            '--disable-features=VizDisplayCompositor',
                            '--font-render-hinting=none',
                            '--disable-font-subpixel-positioning'
                        ]
                    )
                    page = await browser.new_page()
                    
                    # Set viewport size for better screenshot quality | 设置视口大小以获得更好的截图质量
                    await page.set_viewport_size({"width": 1200, "height": 800})
                    
                    # Load HTML file | 加载HTML文件
                    await page.goto(f"file://{temp_html_file.absolute()}")
                    
                    # Wait for page to fully load | 等待页面完全加载
                    await page.wait_for_timeout(2000)
                    
                    # Take screenshot | 截图
                    await page.screenshot(path=str(temp_png_file), full_page=True)
                    
                    await browser.close()
                
                # Read PNG file and encode as base64 | 读取PNG文件并编码为base64
                with open(temp_png_file, 'rb') as f:
                    png_data = base64.b64encode(f.read()).decode('utf-8')
                
                print(f"Mind map generated successfully: {temp_png_file}")
                
                return {
                    "success": True,
                    "title": title,
                    "image_data": png_data,
                    "image_format": "png",
                    "temp_file": str(temp_png_file),
                    "size_bytes": len(base64.b64decode(png_data))
                }
                
            except Exception as e:
                error_msg = f"Failed to create mind map: {str(e)}"
                print(f"Error: {error_msg}")
                return {"error": error_msg, "success": False}
        
        @mcp.tool()
        async def save_mind_map(markdown_content: str, filename: str = None) -> dict:
            """Save mind map to output directory | 将思维导图保存到输出目录"""
            try:
                # If no filename specified, use timestamp | 如果没有指定文件名，使用时间戳
                if not filename:
                    filename = f"mindmap_{int(time.time())}"
                
                # Ensure filename doesn't have extension | 确保文件名没有扩展名
                if filename.endswith('.png'):
                    filename = filename[:-4]
                
                # Generate mind map | 生成思维导图
                result = await create_mind_map(markdown_content, filename)
                
                if not result.get("success", False):
                    return result
                
                # Save to output directory | 保存到输出目录
                png_data = base64.b64decode(result["image_data"])
                output_file = self.output_dir / f"{filename}.png"
                
                with open(output_file, 'wb') as f:
                    f.write(png_data)
                
                return {
                    "success": True,
                    "message": f"Mind map saved successfully to: {output_file}",
                    "output_file": str(output_file),
                    "size_bytes": len(png_data)
                }
                
            except Exception as e:
                error_msg = f"Failed to save mind map: {str(e)}"
                print(f"Error: {error_msg}")
                return {"error": error_msg, "success": False}
        
        @mcp.resource("mindmap://examples/{example_name}")
        def get_example(example_name: str) -> str:
            """Get example Markdown content for mind maps | 获取思维导图的示例Markdown内容"""
            examples = {
                "basic": """# My Learning Plan

## Programming
### Frontend Development
- HTML Basics
- CSS Styling
- JavaScript

### Backend Development
- Python
- Databases

## Project Practice
### Personal Projects
- Personal Blog
- Todo Application""",
                
                "company": """# Company Structure

## Executive Team
### CEO
- Strategic Planning
- Board Relations

### CTO
- Technology Strategy
- Team Leadership

## Departments
### Engineering
- Frontend Team
- Backend Team
- DevOps Team

### Marketing
- Content Creation
- Social Media
- Analytics""",
                
                "chinese": """# 刘德华十大经典歌曲

## 早期作品
### 忘情水
- 经典代表作
- 传唱度极高

### 中国人
- 爱国情怀
- 文化认同

## 中期作品
### 冰雨
- 情感真挚
- 旋律优美

### 爱你一万年
- 浪漫情歌
- 深情演绎

## 后期作品
### 一起走过的日子
- 友情赞歌
- 温暖治愈"""
            }
            
            return examples.get(example_name, f"Example '{example_name}' not found. Available: {', '.join(examples.keys())}")
        
        return mcp
    
    
    def run_streamablehttp(self, host: str = None, port: int = None):
        """Run server in streamable HTTP mode | 以可流式HTTP模式运行服务器"""
        import os
        # Use config defaults if not provided | 如果未提供则使用配置默认值
        host = host or Config.HOST
        port = port or Config.STREAMABLE_PORT
        internal_port = Config.FASTMCP_INTERNAL_PORT
        
        # Set environment variables to force host binding | 设置环境变量强制主机绑定
        os.environ['HOST'] = host
        os.environ['UVICORN_HOST'] = host
        print("=" * 50) 
        print("Mind Map MCP Server - Streamable HTTP mode")
        print(f"   Streamable HTTP at http://{host}:{internal_port}/mcp")
        print(f"   External access via port {port} (if using Docker)")
        print(f"   Configuration loaded from environment/config")
        if Config.DEBUG:
            print(f"   Debug mode: ENABLED")
        print("=" * 50)
        
        # 使用FastMCP但通过环境变量强制host绑定
        import uvicorn
        import sys
        from mcp.server.fastmcp import FastMCP
        
        # 创建FastMCP实例
        mcp = self.create_fastmcp_server()
        
        # 获取ASGI应用
        try:
            # 尝试使用streamable-http应用
            app = mcp.streamable_http_app()
            print(f"Starting Uvicorn on {host}:{internal_port}")
            uvicorn.run(app, host=host, port=internal_port)
        except AttributeError:
            # 如果没有streamable_http_app方法，回退到原来的方式
            print("Falling back to mcp.run()")
            mcp.run(transport="streamable-http")
    
    # Keep backward compatibility | 保持向后兼容性
    async def run(self):
        """Default run method (stdio) for backward compatibility | 默认运行方法（stdio）保持向后兼容"""
        await self.run_stdio()


def main():
    """
    Main function with transport selection | 支持传输方式选择的主函数
    """
    parser = argparse.ArgumentParser(description="Mind Map MCP Server with multiple transport support")
    
    # Transport selection | 传输方式选择
    parser.add_argument(
        "transport", 
        choices=["stdio", "streamablehttp", "streamable-http"],
        nargs='?',  # Make it optional for backward compatibility
        default="stdio",
        help="Transport protocol to use (default: stdio)"
    )
    
    # Host and port for network transports | 网络传输的主机和端口 
    parser.add_argument("--host", default=Config.HOST, 
                       help=f"Host to bind to (default: {Config.HOST}, configurable via HOST env var)")
    parser.add_argument("--port", type=int, 
                       help="Port to bind to (default from config: Streamable={})".format(
                           Config.STREAMABLE_PORT))
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Mind Map MCP Server - Multi-transport Support")
    print("   Turn your ideas into visual mind maps")
    print("=" * 60)
    print("Configuration Summary | 配置摘要:")
    print(f"   Host: {Config.HOST}")
    print(f"   Streamable Port: {Config.STREAMABLE_PORT}")  
    print(f"   Debug Mode: {'ON' if Config.DEBUG else 'OFF'}")
    print(f"   Log Level: {Config.LOG_LEVEL}")
    print("=" * 60)
    
    # Check dependencies | 检查依赖
    if not _check_dependencies():
        return 1
    
    # Create server instance | 创建服务器实例
    server = MindMapServer()
    
    try:
        if args.transport == "stdio":
            asyncio.run(server.run_stdio())
        elif args.transport in ["streamablehttp", "streamable-http"]:
            port = args.port or Config.STREAMABLE_PORT
            server.run_streamablehttp(host=args.host, port=port)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return 1
    
    return 0


def _check_dependencies():
    """Check if necessary dependencies are installed | 检查是否安装了必要的依赖"""
    print("Checking dependencies...")
    
    # Check Node.js and markmap-cli | 检查Node.js和markmap-cli
    try:
        result = subprocess.run(['npx', '--version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("Please install Node.js and npm first")
            return False
        print("Node.js installed")
    except FileNotFoundError:
        print("Please install Node.js and npm first")
        return False
    
    # Check Playwright | 检查Playwright
    try:
        result = subprocess.run(['playwright', '--version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("Please run: playwright install chromium")
            return False
        print("Playwright installed")
    except FileNotFoundError:
        print("Please install and configure Playwright first")
        return False
    
    print("All dependencies check passed")
    return True


if __name__ == "__main__":
    sys.exit(main())