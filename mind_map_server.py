"""
Mind Map MCP Server | 思维导图MCP服务器
==========================================================

This file is the core of the mind map service, acting as an intelligent assistant that:
1. Receives your text descriptions (Markdown format)
2. Converts text into beautiful mind maps
3. Saves mind maps as PNG images for you

Simply put: you give it text, it gives you pictures!

这个文件是思维导图服务的核心，充当智能助手：
1. 接收你的文本描述（Markdown格式）
2. 将文本转换为美观的思维导图
3. 将思维导图保存为PNG图片

简单来说：你给它文字，它给你图片！
"""

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

# MCP related imports - tools that enable the service to work with MCP protocol
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
except ImportError:
    print("Please install MCP library: pip install mcp")
    sys.exit(1)

# Browser automation tools - used to convert web pages to images
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Please install Playwright: pip install playwright")
    print("Then run: playwright install chromium")
    sys.exit(1)


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
        """Fix Chinese font support in generated HTML | 修复生成HTML中的中文字体支持"""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Replace the default font-family with Chinese-friendly fonts | 用中文友好字体替换默认字体
            old_font_css = "font-family: ui-sans-serif, system-ui, sans-serif, 'Apple Color Emoji',\n    'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';"
            new_font_css = "font-family: 'Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'WenQuanYi Micro Hei', 'Microsoft YaHei', 'SimHei', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';"
            
            html_content = html_content.replace(old_font_css, new_font_css)
            
            # Also add additional CSS for SVG text elements | 为SVG文本元素添加额外的CSS
            additional_css = """
svg text {
  font-family: 'Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'WenQuanYi Micro Hei', 'Microsoft YaHei', 'SimHei', sans-serif !important;
  font-weight: normal;
}
"""
            
            # Insert additional CSS before </style> | 在</style>之前插入额外的CSS
            html_content = html_content.replace('</style>', additional_css + '</style>')
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            print("Chinese font support added to HTML")
            
        except Exception as e:
            print(f"Warning: Failed to fix Chinese fonts: {e}")

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
    
    async def run(self):
        """Start MCP server | 启动MCP服务器"""
        print("Starting Mind Map MCP Server...")
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


def main():
    """
    Main function - program entry point | 主函数 - 程序入口点
    
    Like the main switch for the entire service | 就像整个服务的总开关
    """
    print("=" * 50)
    print("Mind Map MCP Server")
    print("   Turn your ideas into visual mind maps")
    print("=" * 50)
    
    # Check dependencies | 检查依赖
    if not _check_dependencies():
        return
    
    # Create and run server | 创建并运行服务器
    server = MindMapServer()
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Server error: {e}")


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
    main()