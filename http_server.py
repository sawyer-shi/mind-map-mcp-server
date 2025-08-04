"""
Mind Map MCP HTTP Server | 思维导图MCP HTTP服务器
=======================================================

HTTP transport for Mind Map MCP Server
为思维导图MCP服务器提供HTTP传输协议支持
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add the current directory to Python path to import our server
sys.path.append(str(Path(__file__).parent))

try:
    from fastapi import FastAPI, HTTPException, Request, Response
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError:
    print("Please install: pip install fastapi uvicorn")
    sys.exit(1)

from mind_map_server import MindMapServer


def create_app():
    """Create FastAPI application with MCP protocol support | 创建支持MCP协议的FastAPI应用"""
    
    app = FastAPI(title="Mind Map MCP Server", description="HTTP transport for Mind Map MCP")
    
    # Initialize our mind map server | 初始化思维导图服务器
    server = MindMapServer()
    
    @app.get("/")
    async def root():
        return {
            "message": "Mind Map MCP HTTP Server",
            "version": "1.0.0",
            "mcp_endpoint": "/mcp"
        }
    
    @app.post("/mcp")
    async def mcp_endpoint(request: Request):
        """Handle MCP protocol requests | 处理MCP协议请求"""
        try:
            body = await request.json()
            method = body.get("method")
            request_id = body.get("id")
            params = body.get("params", {})
            
            # Handle MCP initialize request | 处理MCP初始化请求
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "mind-map-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            # Handle notifications/initialized (notification without response)
            # 处理notifications/initialized（无需响应的通知）
            elif method == "notifications/initialized":
                # This is a notification, return empty JSON response for compatibility
                return JSONResponse(status_code=200, content={})
            
            # Handle tools/list request | 处理工具列表请求
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "create_mind_map",
                                "description": "Generate mind map PNG image from Markdown content",
                                "inputSchema": {
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
                            },
                            {
                                "name": "save_mind_map",
                                "description": "Save mind map to file",
                                "inputSchema": {
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
                            }
                        ]
                    }
                }
            
            # Handle tools/call request | 处理工具调用请求
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "create_mind_map":
                    result = await server._create_mind_map(
                        arguments.get("markdown_content", ""),
                        arguments.get("title", "Mind Map")
                    )
                    
                    # Convert MCP result to JSON response | 将MCP结果转换为JSON响应
                    content = []
                    for item in result:
                        if hasattr(item, 'text'):
                            content.append({
                                "type": "text",
                                "text": item.text
                            })
                        elif hasattr(item, 'data'):
                            content.append({
                                "type": "image",
                                "data": item.data,
                                "mimeType": "image/png"
                            })
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": content
                        }
                    }
                
                elif tool_name == "save_mind_map":
                    result = await server._save_mind_map(
                        arguments.get("markdown_content", ""),
                        arguments.get("filename")
                    )
                    
                    # Convert MCP result to JSON response | 将MCP结果转换为JSON响应
                    content = []
                    for item in result:
                        if hasattr(item, 'text'):
                            content.append({
                                "type": "text",
                                "text": item.text
                            })
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": content
                        }
                    }
                
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
            
            # Handle ping (keep-alive) | 处理ping（保持连接）
            elif method == "ping":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {}
                }
            
            else:
                # Check if this is a notification (no id) | 检查是否为通知（无id）
                if request_id is None:
                    # Notifications should return empty JSON for compatibility
                    return JSONResponse(status_code=200, content={})
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                
        except Exception as e:
            # Ensure we have a valid ID for error response | 确保错误响应有有效的ID
            error_id = None
            try:
                error_id = body.get("id") if "body" in locals() and body else None
            except:
                pass
                
            return {
                "jsonrpc": "2.0",
                "id": error_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    return app


def main():
    """Main function to start HTTP MCP server | 启动HTTP MCP服务器的主函数"""
    
    # Get configuration from environment | 从环境变量获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("FASTMCP_PORT", "8090"))
    
    print("=" * 50)
    print("Mind Map MCP HTTP Server")
    print("   HTTP transport for Mind Map MCP")
    print("=" * 50)
    print(f"Starting server at: http://{host}:{port}")
    print("MCP endpoint: http://localhost:8090/mcp")
    print("Available tools:")
    print("   - create_mind_map: Generate mind map PNG")
    print("   - save_mind_map: Save mind map to file")
    print("=" * 50)
    
    # Create and run the app | 创建并运行应用
    app = create_app()
    
    # Start the server | 启动服务器
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()