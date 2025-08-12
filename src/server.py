"""
Mind Map MCP Server | 思维导图MCP服务器
=====================================

Main server class that handles different transport protocols.
处理不同传输协议的主要服务器类。
"""

import asyncio
import os
import uvicorn
from pathlib import Path
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config import Config
from mind_map_generator import MindMapGenerator
from mcp_tools import MCPTools, FastMCPTools


class MindMapServer:
    """
    Mind Map Server Class | 思维导图服务器类
    
    Main server that coordinates all components and handles different transport protocols.
    协调所有组件并处理不同传输协议的主服务器。
    """
    
    def __init__(self):
        # Create necessary directories | 创建必要目录
        self.temp_dir = Path("temp")
        self.output_dir = Path("output")
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize generator and tools | 初始化生成器和工具
        self.generator = MindMapGenerator(self.temp_dir, self.output_dir)
        self.mcp_tools = MCPTools(self.generator)
        self.fastmcp_tools = FastMCPTools(self.generator)
        
        # Initialize servers | 初始化服务器
        self.stdio_server = None
        self.fastmcp_server = None
    
    def create_stdio_server(self) -> Server:
        """
        Create stdio MCP server | 创建stdio MCP服务器
        """
        if self.stdio_server is None:
            self.stdio_server = Server("mind-map-server")
            
            # Register tools | 注册工具
            for tool in self.mcp_tools.get_tool_definitions():
                @self.stdio_server.call_tool()
                async def handle_tool(name: str, arguments: dict):
                    return await self.mcp_tools.handle_tool_call(name, arguments)
            
            # Register initialization handler | 注册初始化处理器
            @self.stdio_server.set_logging_level()
            async def handle_logging_level(level):
                print(f"Logging level set to: {level}")
        
        return self.stdio_server
    
    def create_fastmcp_server(self) -> FastMCP:
        """
        Create FastMCP server for HTTP transport | 创建用于HTTP传输的FastMCP服务器
        """
        if self.fastmcp_server is None:
            self.fastmcp_server = FastMCP("Mind Map MCP Server")
            
            # Register tools with FastMCP | 使用FastMCP注册工具
            self.fastmcp_tools.register_tools(self.fastmcp_server)
        
        return self.fastmcp_server
    
    def create_mcp_app(self) -> FastAPI:
        """
        Create FastAPI app for MCP service only | 创建仅用于MCP服务的FastAPI应用
        """
        # Get FastMCP instance | 获取FastMCP实例
        fastmcp_instance = self.create_fastmcp_server()
        
        # Get the ASGI app from FastMCP | 从FastMCP获取ASGI应用
        mcp_app = getattr(fastmcp_instance, 'streamable_http_app', None)
        
        if mcp_app is None:
            raise RuntimeError("Unable to get streamable_http_app from FastMCP instance")
        
        # Create main FastAPI app | 创建主FastAPI应用
        app = FastAPI(
            title="Mind Map MCP Server",
            description="Convert Markdown to mind map images with multi-cloud storage support",
            version="1.0.0"
        )
        
        # Add CORS middleware | 添加CORS中间件
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Mount MCP app | 挂载MCP应用
        app.mount("/mcp", mcp_app)
        
        # Add root endpoint | 添加根端点
        @app.get("/")
        async def root():
            return {
                "name": "Mind Map MCP Server",
                "version": "1.0.0",
                "description": "Convert Markdown to mind map images",
                "endpoints": {
                    "mcp": f"http://{Config.LOCAL_HOST}:{Config.STREAMABLE_PORT}/mcp",
                    "static_files": f"http://{Config.LOCAL_HOST}:{Config.STATIC_FILE_PORT}/output",
                    "health": f"http://{Config.LOCAL_HOST}:{Config.STREAMABLE_PORT}/health"
                },
                "storage_info": self.generator.storage_manager.get_storage_info()
            }
        
        # Add health check endpoint | 添加健康检查端点
        @app.get("/health")
        async def health():
            return {"status": "healthy", "service": "mind-map-mcp-server"}
        
        return app
    
    def create_static_file_app(self) -> FastAPI:
        """
        Create FastAPI app for static file serving only | 创建仅用于静态文件服务的FastAPI应用
        """
        app = FastAPI(
            title="Mind Map Static File Server",
            description="Static file server for mind map images",
            version="1.0.0"
        )
        
        # Add CORS middleware | 添加CORS中间件
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Mount static files for output directory | 挂载输出目录的静态文件服务
        if self.output_dir.exists():
            app.mount("/output", StaticFiles(directory=str(self.output_dir)), name="output")
            print(f"Static files mounted at /output -> {self.output_dir}")
        
        # Add root endpoint | 添加根端点
        @app.get("/")
        async def root():
            return {
                "name": "Mind Map Static File Server",
                "version": "1.0.0",
                "description": "Static file server for mind map images",
                "output_directory": str(self.output_dir),
                "endpoints": {
                    "static_files": "/output"
                }
            }
        
        return app
    
    async def run_stdio(self):
        """
        Run server in stdio mode | 以stdio模式运行服务器
        """
        print("Starting Mind Map MCP Server in stdio mode...")
        print("Server ready for MCP connections via stdin/stdout")
        
        server = self.create_stdio_server()
        
        # Run stdio server | 运行stdio服务器
        from mcp.server.stdio import stdio_server
        async with stdio_server(server) as streams:
            await server.run(
                streams[0], streams[1], 
                InitializationOptions(
                    server_name="mind-map-server",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
    
    async def run_fastmcp(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Run server in FastMCP HTTP mode | 以FastMCP HTTP模式运行服务器
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        print(f"Starting Mind Map MCP Server on {host}:{port}...")
        
        # Get FastMCP instance and run with uvicorn | 获取FastMCP实例并用uvicorn运行
        fastmcp_instance = self.create_fastmcp_server()
        
        # Use uvicorn to run the FastMCP streamable HTTP app | 使用uvicorn运行FastMCP流式HTTP应用
        import uvicorn
        config = uvicorn.Config(
            app=fastmcp_instance.streamable_http_app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    def run_sync_fastmcp(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Run FastMCP server synchronously | 同步运行FastMCP服务器
        """
        asyncio.run(self.run_fastmcp(host, port))
    
    def get_server_info(self) -> dict:
        """
        Get server information | 获取服务器信息
        """
        return {
            "name": "Mind Map MCP Server",
            "version": "1.0.0",
            "description": "Convert Markdown to mind map images",
            "author": "sawyer-shi",
            "transport_protocols": ["stdio", "fastmcp"],
            "tools": [tool.name for tool in self.mcp_tools.get_tool_definitions()]
        }