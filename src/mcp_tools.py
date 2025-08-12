"""
MCP Tools | MCP工具
===================

MCP tool definitions and handlers for the Mind Map server.
思维导图服务器的MCP工具定义和处理程序。
"""

import base64
import time
from typing import Any, Sequence
from mcp.types import Tool, TextContent, ImageContent

from mind_map_generator import MindMapGenerator
from utils import validate_markdown_content


class MCPTools:
    """
    MCP Tools handler class | MCP工具处理类
    
    Manages all MCP tool definitions and their implementations.
    管理所有MCP工具定义及其实现。
    """
    
    def __init__(self, generator: MindMapGenerator):
        self.generator = generator
    
    def get_tool_definitions(self) -> list[Tool]:
        """Return list of all available tools | 返回所有可用工具列表"""
        return [
            Tool(
                name="create_mind_map",
                description="Create a mind map PNG image from Markdown content and store it using configured storage provider (local, Aliyun OSS, Huawei OceanStor, MinIO, Amazon S3, Azure Blob, or Google Cloud Storage)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "markdown_content": {
                            "type": "string",
                            "description": "Markdown formatted text to convert to mind map"
                        },
                        "title": {
                            "type": "string",
                            "description": "Optional title for the mind map",
                            "default": "Mind Map"
                        }
                    },
                    "required": ["markdown_content"]
                }
            ),
            Tool(
                name="list_images",
                description="List all generated mind map images from the output directory",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]
    
    async def handle_tool_call(self, name: str, arguments: dict) -> Sequence[TextContent | ImageContent]:
        """
        Handle tool calls | 处理工具调用
        
        Args:
            name: Tool name to execute
            arguments: Tool arguments
            
        Returns:
            List of content objects (text or image)
        """
        try:
            if name == "create_mind_map":
                return await self._handle_create_mind_map(arguments)
            elif name == "list_images":
                return await self._handle_list_images(arguments)
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
                
        except Exception as e:
            return [TextContent(
                type="text", 
                text=f"Error executing {name}: {str(e)}"
            )]
    
    async def _handle_create_mind_map(self, arguments: dict) -> Sequence[TextContent | ImageContent]:
        """Handle create_mind_map tool | 处理create_mind_map工具"""
        markdown_content = arguments.get("markdown_content", "")
        title = arguments.get("title", "Mind Map")
        
        # Validate markdown content | 验证markdown内容
        is_valid, error_msg = validate_markdown_content(markdown_content)
        if not is_valid:
            return [TextContent(
                type="text",
                text=f"Error: {error_msg}"
            )]
        
        # Generate mind map | 生成思维导图
        result = await self.generator.generate_mind_map(markdown_content, title)
        
        if result["success"]:
            # Create response text with storage information | 创建包含存储信息的响应文本
            response_text = f"Mind map '{title}' created successfully!"
            if result.get("storage_url"):
                response_text += f"\n🔗 Storage URL: {result['storage_url']}"
                response_text += f"\n📁 Storage Type: {result.get('storage_type', 'local')}"
                if result.get("storage_message"):
                    response_text += f"\n💾 {result['storage_message']}"
            
            return [
                TextContent(
                    type="text",
                    text=response_text
                ),
                ImageContent(
                    type="image",
                    data=result["image_data"],
                    mimeType="image/png"
                )
            ]
        else:
            return [TextContent(
                type="text",
                text=f"Failed to create mind map: {result['error']}"
            )]
    
    async def _handle_list_images(self, arguments: dict) -> Sequence[TextContent]:
        """Handle list_images tool | 处理list_images工具"""
        try:
            # Get list of images from the output directory | 从输出目录获取图像列表
            import os
            from pathlib import Path
            
            output_dir = self.generator.output_dir
            if not output_dir.exists():
                return [TextContent(
                    type="text",
                    text="No images found. Output directory does not exist."
                )]
            
            # Find all PNG files recursively | 递归查找所有PNG文件
            image_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.lower().endswith('.png'):
                        full_path = Path(root) / file
                        rel_path = full_path.relative_to(output_dir)
                        # Get file stats | 获取文件统计信息
                        stat = full_path.stat()
                        image_files.append({
                            'filename': file,
                            'path': str(rel_path),
                            'size': stat.st_size,
                            'modified': stat.st_mtime
                        })
            
            if not image_files:
                return [TextContent(
                    type="text",
                    text="No mind map images found in the output directory."
                )]
            
            # Sort by modification time (newest first) | 按修改时间排序（最新的在前）
            image_files.sort(key=lambda x: x['modified'], reverse=True)
            
            # Format response | 格式化响应
            response_lines = [f"Found {len(image_files)} mind map images:"]
            for i, img in enumerate(image_files[:20], 1):  # Show max 20 images
                size_kb = img['size'] / 1024
                import time
                mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(img['modified']))
                response_lines.append(f"{i}. {img['filename']} ({size_kb:.1f} KB, {mod_time})")
                response_lines.append(f"   Path: {img['path']}")
            
            if len(image_files) > 20:
                response_lines.append(f"... and {len(image_files) - 20} more images")
            
            return [TextContent(
                type="text",
                text="\n".join(response_lines)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error listing images: {str(e)}"
            )]


class FastMCPTools:
    """
    FastMCP Tools handler class | FastMCP工具处理类
    
    Handles tool registration and execution for FastMCP server.
    处理FastMCP服务器的工具注册和执行。
    """
    
    def __init__(self, generator: MindMapGenerator):
        self.generator = generator
    
    def register_tools(self, app):
        """Register tools with FastMCP app | 向FastMCP应用注册工具"""
        
        # Register custom tools to provide direct image access | 注册自定义工具提供直接图片访问
        @app.tool()
        async def list_images() -> dict:
            """List all generated mind map images | 列出所有生成的思维导图图片"""
            import os
            from datetime import datetime
            
            output_dir = self.generator.output_dir
            if not output_dir.exists():
                return {"images": [], "message": "No images found"}
            
            images = []
            for file_path in output_dir.glob("*.png"):
                stat = file_path.stat()
                images.append({
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "file_path": str(file_path)
                })
            
            images.sort(key=lambda x: x["created"], reverse=True)  # Latest first
            return {
                "images": images,
                "count": len(images),
                "message": f"Found {len(images)} mind map images"
            }
        
        @app.tool()
        async def create_mind_map(markdown_content: str, title: str = "Mind Map") -> dict:
            """
            Create a mind map PNG image from Markdown content
            从Markdown内容创建思维导图PNG图片
            
            Args:
                markdown_content: Markdown formatted text to convert
                title: Optional title for the mind map
                
            Returns:
                dict: Result with success status and image data
            """
            # Validate markdown content | 验证markdown内容
            is_valid, error_msg = validate_markdown_content(markdown_content)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg,
                    "image_data": None
                }
            
            result = await self.generator.generate_mind_map(markdown_content, title)
            
            response = {
                "success": result["success"],
                "error": result.get("error"),
                "image_data": result.get("image_data"),
                "storage_url": result.get("storage_url"),
                "storage_type": result.get("storage_type"),
                "storage_message": result.get("storage_message")
            }
            
            if result["success"]:
                response["message"] = f"Mind map '{title}' created and saved successfully!"
                if result.get("storage_url"):
                    response["message"] += f" Storage URL: {result['storage_url']}"
                # Add storage information to response | 添加存储信息到响应
                response["storage_url"] = result.get("storage_url")
                response["storage_type"] = result.get("storage_type")
                response["storage_message"] = result.get("storage_message")
            else:
                response["message"] = f"Failed to create mind map: {result.get('error')}"
                
            return response
        
        @app.tool()
        async def list_images() -> dict:
            """
            List all generated mind map images
            列出所有生成的思维导图图像
            
            Returns:
                dict: Result with list of images and metadata
            """
            try:
                import os
                from pathlib import Path
                
                output_dir = self.generator.output_dir
                if not output_dir.exists():
                    return {
                        "success": True,
                        "images": [],
                        "message": "No images found. Output directory does not exist."
                    }
                
                # Find all PNG files recursively | 递归查找所有PNG文件
                image_files = []
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        if file.lower().endswith('.png'):
                            full_path = Path(root) / file
                            rel_path = full_path.relative_to(output_dir)
                            # Get file stats | 获取文件统计信息
                            stat = full_path.stat()
                            image_files.append({
                                'filename': file,
                                'path': str(rel_path),
                                'size': stat.st_size,
                                'modified': stat.st_mtime
                            })
                
                # Sort by modification time (newest first) | 按修改时间排序（最新的在前）
                image_files.sort(key=lambda x: x['modified'], reverse=True)
                
                return {
                    "success": True,
                    "images": image_files,
                    "count": len(image_files),
                    "message": f"Found {len(image_files)} mind map images"
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "images": [],
                    "error": str(e),
                    "message": f"Error listing images: {str(e)}"
                }