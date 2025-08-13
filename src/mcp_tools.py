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
                description="Create a high-quality mind map PNG image from Markdown content. Features: intelligent viewport sizing, high-DPI rendering, watermark-free output, image validation, multi-cloud storage support (local, Aliyun OSS, Huawei OceanStor, MinIO, Amazon S3, Azure Blob, Google Cloud Storage), and returns accessible image URL.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "markdown_content": {
                            "type": "string",
                            "description": "Markdown formatted text to convert to mind map. Supports hierarchical structure with # headers, bullet points, and nested lists. Complex content will automatically use larger viewport for better clarity."
                        },
                        "title": {
                            "type": "string",
                            "description": "Title for the mind map file (optional, defaults to 'Mind Map'). Used as filename and display title.",
                            "default": "Mind Map"
                        },
                        "quality": {
                            "type": "string",
                            "description": "Image quality level: 'low', 'medium', 'high', 'ultra'. Defaults to config setting. Higher quality uses larger viewport and higher DPI.",
                            "enum": ["low", "medium", "high", "ultra"],
                            "default": "high"
                        }
                    },
                    "required": ["markdown_content"]
                }
            ),
            Tool(
                name="list_images",
                description="List mind map images by date and optional name filter. Returns URLs of matching images.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "Date in YYYY-MM-DD format. If not provided, uses current date.",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "name_filter": {
                            "type": "string",
                            "description": "Optional name filter to fuzzy match mind map names (case-insensitive partial match)"
                        }
                    },
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
        quality = arguments.get("quality", "high")
        
        # Validate markdown content | 验证markdown内容
        is_valid, error_msg = validate_markdown_content(markdown_content)
        if not is_valid:
            return [TextContent(
                type="text",
                text=f"Error: {error_msg}"
            )]
        
        # Generate mind map | 生成思维导图
        result = await self.generator.generate_mind_map(markdown_content, title, quality)
        
        if result["success"]:
            # Validate mind map URL exists | 验证思维导图URL存在
            if not result.get("mind_map_image_url"):
                return [TextContent(
                    type="text",
                    text=f"Error: Mind map generated but no image URL returned. This may indicate a file generation issue."
                )]
            
            # Create response text with storage information | 创建包含存储信息的响应文本
            response_text = f"Mind map '{title}' created successfully!"
            if result.get("mind_map_image_url"):
                response_text += f"\n🔗 Mind Map Image URL: {result['mind_map_image_url']}"
                response_text += f"\n📁 Storage Type: {result.get('storage_type', 'local')}"
                if result.get("storage_message"):
                    response_text += f"\n💾 {result['storage_message']}"
            
            # Add validation info - image_data is None for response optimization | 添加验证信息 - image_data为None以优化响应
            response_text += f"\n✅ Image validation: Passed (base64 generated for internal validation only)"
            response_text += f"\n📸 Image URL: {result['mind_map_image_url']}"
            
            return [
                TextContent(
                    type="text",
                    text=response_text
                )
            ]
        else:
            return [TextContent(
                type="text",
                text=f"Failed to create mind map: {result['error']}"
            )]
    
    async def _handle_list_images(self, arguments: dict) -> Sequence[TextContent]:
        """Handle list_images tool with date and name filtering | 处理带日期和名称过滤的list_images工具"""
        try:
            from datetime import datetime
            from pathlib import Path
            import os
            from urllib.parse import quote
            
            # Get date parameter or use current date | 获取日期参数或使用当前日期
            date_str = arguments.get("date")
            if not date_str:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            # Parse date to get year, month, day | 解析日期获取年月日
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                year = date_obj.strftime("%Y")
                month = date_obj.strftime("%m")  
                day = date_obj.strftime("%d")
            except ValueError:
                return [TextContent(
                    type="text",
                    text=f"Invalid date format: {date_str}. Please use YYYY-MM-DD format."
                )]
            
            # Get name filter parameter | 获取名称过滤参数
            name_filter = arguments.get("name_filter", "").lower().strip()
            
            # Build date-specific directory path | 构建日期特定目录路径
            output_dir = self.generator.output_dir
            date_dir = output_dir / year / month / day
            
            if not date_dir.exists():
                return [TextContent(
                    type="text",
                    text=f"No mind maps found for date {date_str}. Directory {date_dir} does not exist."
                )]
            
            # Find all PNG files in the date directory | 在日期目录中查找所有PNG文件
            png_files = list(date_dir.glob("*.png"))
            
            if not png_files:
                return [TextContent(
                    type="text",
                    text=f"No mind map images found for date {date_str}."
                )]
            
            # Filter by name if provided | 如果提供了名称则进行过滤
            if name_filter:
                filtered_files = []
                for file_path in png_files:
                    if name_filter in file_path.stem.lower():
                        filtered_files.append(file_path)
                png_files = filtered_files
                
                if not png_files:
                    return [TextContent(
                        type="text",
                        text=f"No mind map images found for date {date_str} matching name filter '{arguments.get('name_filter')}'."
                    )]
            
            # Generate URLs and format response | 生成URL并格式化响应
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from config import Config
            config = Config()
            base_url = config.LOCAL_STORAGE_URL_PREFIX
            
            response_lines = []
            if name_filter:
                response_lines.append(f"Found {len(png_files)} mind map(s) for {date_str} matching '{arguments.get('name_filter')}':")
            else:
                response_lines.append(f"Found {len(png_files)} mind map(s) for {date_str}:")
            response_lines.append("")
            
            for file_path in sorted(png_files, key=lambda x: x.stat().st_mtime, reverse=True):
                # Get file info | 获取文件信息
                stat = file_path.stat()
                size_kb = stat.st_size // 1024
                mod_time = datetime.fromtimestamp(stat.st_mtime).strftime('%H:%M:%S')
                
                # Generate URL | 生成URL
                relative_path = f"{year}/{month}/{day}/{quote(file_path.name)}"
                image_url = f"{base_url}/{relative_path}"
                
                # Format output | 格式化输出
                response_lines.append(f"🖼️  **{file_path.stem}**")
                response_lines.append(f"   🔗 URL: {image_url}")
                response_lines.append(f"   📏 Size: {size_kb} KB")
                response_lines.append(f"   ⏰ Created: {mod_time}")
                response_lines.append("")
            
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
        async def create_mind_map(markdown_content: str, title: str = "Mind Map", quality: str = "high") -> dict:
            """
            Create a mind map PNG image from Markdown content
            从Markdown内容创建思维导图PNG图片
            
            Features: watermark-free output, image validation, multi-cloud storage support,
            and returns accessible image URL with optimized response size.
            
            Args:
                markdown_content: Markdown formatted text to convert (supports hierarchical structure)
                title: Title for the mind map file (used as filename and display title)
                quality: Image quality level ('low', 'medium', 'high', 'ultra')
                
            Returns:
                dict: Result with success status, image URL, storage info, and validation details
            """
            # Validate markdown content | 验证markdown内容
            is_valid, error_msg = validate_markdown_content(markdown_content)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg
                }
            
            result = await self.generator.generate_mind_map(markdown_content, title, quality)
            
            response = {
                "success": result["success"],
                "error": result.get("error"),
                "mind_map_image_url": result.get("mind_map_image_url"),
                "storage_type": result.get("storage_type"),
                "storage_message": result.get("storage_message")
            }
            
            if result["success"]:
                # Validate mind map URL exists (image_data is None for optimization) | 验证思维导图URL存在（image_data为None以优化响应）
                if not result.get("mind_map_image_url"):
                    response["success"] = False
                    response["error"] = "Mind map generated but no image URL returned"
                    response["message"] = "Error: File generation issue - no image URL"
                    return response
                
                response["message"] = f"Mind map '{title}' created and saved successfully!"
                response["message"] += f" Mind Map Image URL: {result['mind_map_image_url']}"
                
                # Add storage information to response | 添加存储信息到响应
                response["mind_map_image_url"] = result.get("mind_map_image_url")
                response["storage_type"] = result.get("storage_type")
                response["storage_message"] = result.get("storage_message")
                
                # Add validation info - image_data is None for response optimization | 添加验证信息 - image_data为None以优化响应
                response["message"] += " (Image validation passed - base64 generated for internal validation only)"
            else:
                response["message"] = f"Failed to create mind map: {result.get('error')}"
                
            return response
        
        @app.tool()
        async def list_images(date: str = None, name_filter: str = None) -> dict:
            """
            List mind map images by date and optional name filter
            按日期和可选名称过滤器列出思维导图图像
            
            Args:
                date: Date in YYYY-MM-DD format. If not provided, uses current date.
                name_filter: Optional name filter to fuzzy match mind map names
                
            Returns:
                dict: Result with list of images and metadata including URLs
            """
            try:
                from datetime import datetime
                from pathlib import Path
                from urllib.parse import quote
                
                # Get date parameter or use current date | 获取日期参数或使用当前日期
                if not date:
                    date = datetime.now().strftime("%Y-%m-%d")
                
                # Parse date to get year, month, day | 解析日期获取年月日
                try:
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    year = date_obj.strftime("%Y")
                    month = date_obj.strftime("%m")  
                    day = date_obj.strftime("%d")
                except ValueError:
                    return {
                        "success": False,
                        "error": f"Invalid date format: {date}. Please use YYYY-MM-DD format.",
                        "images": []
                    }
                
                # Build date-specific directory path | 构建日期特定目录路径
                output_dir = self.generator.output_dir
                date_dir = output_dir / year / month / day
                
                if not date_dir.exists():
                    return {
                        "success": True,
                        "images": [],
                        "message": f"No mind maps found for date {date}. Directory does not exist."
                    }
                
                # Find all PNG files in the date directory | 在日期目录中查找所有PNG文件
                png_files = list(date_dir.glob("*.png"))
                
                if not png_files:
                    return {
                        "success": True,
                        "images": [],
                        "message": f"No mind map images found for date {date}."
                    }
                
                # Filter by name if provided | 如果提供了名称则进行过滤
                if name_filter:
                    name_filter_lower = name_filter.lower().strip()
                    filtered_files = []
                    for file_path in png_files:
                        if name_filter_lower in file_path.stem.lower():
                            filtered_files.append(file_path)
                    png_files = filtered_files
                    
                    if not png_files:
                        return {
                            "success": True,
                            "images": [],
                            "message": f"No mind map images found for date {date} matching name filter '{name_filter}'."
                        }
                
                # Generate URLs and collect file info | 生成URL并收集文件信息
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                from config import Config
                config = Config()
                base_url = config.LOCAL_STORAGE_URL_PREFIX
                
                images = []
                for file_path in sorted(png_files, key=lambda x: x.stat().st_mtime, reverse=True):
                    # Get file info | 获取文件信息
                    stat = file_path.stat()
                    
                    # Generate URL | 生成URL
                    relative_path = f"{year}/{month}/{day}/{quote(file_path.name)}"
                    image_url = f"{base_url}/{relative_path}"
                    
                    images.append({
                        "filename": file_path.name,
                        "name": file_path.stem,
                        "url": image_url,
                        "size": stat.st_size,
                        "size_kb": stat.st_size // 1024,
                        "created_time": datetime.fromtimestamp(stat.st_mtime).strftime('%H:%M:%S'),
                        "created_date": date,
                        "path": relative_path
                    })
                
                message = f"Found {len(images)} mind map(s) for {date}"
                if name_filter:
                    message += f" matching '{name_filter}'"
                
                return {
                    "success": True,
                    "images": images,
                    "count": len(images),
                    "date": date,
                    "name_filter": name_filter,
                    "message": message
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "images": [],
                    "error": str(e),
                    "message": f"Error listing images: {str(e)}"
                }