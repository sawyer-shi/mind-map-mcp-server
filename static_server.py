#!/usr/bin/env python3
"""
Static File Server for Mind Map MCP Server
静态文件服务器 - 思维导图MCP服务器

This server provides HTTP access to generated mind map files.
此服务器提供对生成的思维导图文件的HTTP访问。
"""

import asyncio
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Import configuration | 导入配置
from src.config import Config


def create_static_server_app(output_dir: Path) -> FastAPI:
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
    if output_dir.exists():
        app.mount("/output", StaticFiles(directory=str(output_dir)), name="output")
        print(f"Static files mounted at /output -> {output_dir}")
    else:
        print(f"Warning: Output directory does not exist: {output_dir}")
    
    # Add root endpoint | 添加根端点
    @app.get("/")
    async def root():
        return {
            "name": "Mind Map Static File Server",
            "version": "1.0.0",
            "description": "Static file server for mind map images",
            "output_directory": str(output_dir),
            "endpoints": {
                "static_files": "/output"
            },
            "config": {
                "host": Config.HOST,
                "port": Config.STATIC_FILE_PORT,
                "mcp_server": f"http://{Config.LOCAL_HOST}:{Config.STREAMABLE_PORT}"
            }
        }
    
    # Add health check endpoint | 添加健康检查端点
    @app.get("/health")
    async def health():
        return {
            "status": "healthy", 
            "service": "mind-map-static-server",
            "output_directory_exists": output_dir.exists()
        }
    
    return app


async def run_static_server():
    """
    Run the static file server | 运行静态文件服务器
    """
    # Setup output directory | 设置输出目录
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    print(f"Starting Mind Map Static File Server...")
    print(f"Host: {Config.HOST}")
    print(f"Port: {Config.STATIC_FILE_PORT}")
    print(f"Output Directory: {output_dir.absolute()}")
    
    # Create static file app | 创建静态文件应用
    app = create_static_server_app(output_dir)
    
    # Configure uvicorn | 配置uvicorn
    config = uvicorn.Config(
        app=app,
        host=Config.HOST,
        port=Config.STATIC_FILE_PORT,
        log_level="info"
    )
    
    # Create and run server | 创建并运行服务器
    server = uvicorn.Server(config)
    await server.serve()


def main():
    """
    Main entry point | 主入口点
    """
    try:
        asyncio.run(run_static_server())
    except KeyboardInterrupt:
        print("\nShutting down static file server...")
    except Exception as e:
        print(f"Error running static file server: {e}")


if __name__ == "__main__":
    main()
