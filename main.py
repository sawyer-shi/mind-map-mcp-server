#!/usr/bin/env python3
"""
Mind Map MCP Server Main Entry Point | 思维导图MCP服务器主入口
=============================================================

This is the new main entry point for the modular Mind Map MCP Server.
这是模块化思维导图MCP服务器的新主入口。
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add src to path for imports | 将src添加到路径以便导入
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables from .env file if available | 如果可用，从.env文件加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.server import MindMapServer


def create_argument_parser():
    """Create command line argument parser | 创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Mind Map MCP Server - Convert Markdown to mind map images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples | 示例:
  %(prog)s stdio                           # Run in stdio mode | 以stdio模式运行
  %(prog)s streamable-http                 # Run in streamable HTTP mode | 以流式HTTP模式运行
  %(prog)s streamable-http --port 8080     # Custom port | 自定义端口
  %(prog)s streamable-http --host 127.0.0.1 # Custom host | 自定义主机
        """
    )
    
    parser.add_argument(
        "transport",
        choices=["stdio", "streamable-http"],
        help="Transport protocol to use | 使用的传输协议"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (streamable-http only) | 绑定的主机地址（仅限流式HTTP）"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (streamable-http only) | 绑定的端口（仅限流式HTTP）"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode | 启用调试模式"
    )
    
    return parser


async def main():
    """Main function | 主函数"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Create server instance | 创建服务器实例
    server = MindMapServer()
    
    try:
        if args.transport == "stdio":
            print("Starting Mind Map MCP Server in stdio mode...")
            print("思维导图MCP服务器正在以stdio模式启动...")
            await server.run_stdio()
            
        elif args.transport == "streamable-http":
            print(f"Starting Mind Map MCP Server in streamable HTTP mode on {args.host}:{args.port}...")
            print(f"思维导图MCP服务器正在以流式HTTP模式启动，地址：{args.host}:{args.port}...")
            await server.run_fastmcp(host=args.host, port=args.port)
            
    except KeyboardInterrupt:
        print("\nServer stopped by user | 服务器被用户停止")
    except Exception as e:
        print(f"Error starting server | 服务器启动错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())