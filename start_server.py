#!/usr/bin/env python3
"""
Mind Map MCP Server Startup Script | 思维导图MCP服务器启动脚本
=============================================================

This script makes starting the service super simple, like clicking a button!
It automatically checks all necessary dependencies and then starts the service.

这个脚本让启动服务变得超级简单，就像点击一个按钮一样！
它会自动检查所有必要的依赖，然后启动服务。
"""

import subprocess
import sys
import os
from pathlib import Path


def print_header():
    """Print welcome message | 打印欢迎信息"""
    print("=" * 60)
    print("🧠 Mind Map MCP Server")
    print("   Transform your ideas into visual mind maps")
    print("=" * 60)
    print()


def check_python():
    """Check Python version | 检查Python版本"""
    print("🐍 Checking Python environment...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version OK: {version.major}.{version.minor}.{version.micro}")
    return True


def check_node():
    """Check Node.js environment | 检查Node.js环境"""
    print("📦 Checking Node.js environment...")
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js version: {version}")
            return True
        else:
            print("❌ Node.js is not properly installed")
            return False
    except FileNotFoundError:
        print("❌ Node.js is not installed")
        print("   Please download and install Node.js from https://nodejs.org")
        return False


def install_python_deps():
    """Install Python dependencies | 安装Python依赖"""
    print("📚 Checking Python dependencies...")
    try:
        # Check if requirements.txt exists | 检查是否有requirements.txt
        if not Path("requirements.txt").exists():
            print("❌ requirements.txt file not found")
            return False
        
        # Install dependencies | 安装依赖
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Python dependencies installed successfully")
            return True
        else:
            print("❌ Failed to install Python dependencies")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error installing Python dependencies: {e}")
        return False


def install_node_deps():
    """Install Node.js dependencies | 安装Node.js依赖"""
    print("🛠️ Installing mind map tools...")
    try:
        result = subprocess.run([
            'npm', 'install', '-g', 'markmap-cli'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Mind map tools installed successfully")
            return True
        else:
            print("❌ Failed to install mind map tools")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error installing mind map tools: {e}")
        return False


def install_playwright():
    """Install Playwright browser | 安装Playwright浏览器"""
    print("🎭 Installing browser for screenshot capture...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'playwright', 'install', 'chromium'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Browser installed successfully")
            return True
        else:
            print("❌ Failed to install browser")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error installing browser: {e}")
        return False


def create_directories():
    """Create necessary directories | 创建必要的目录"""
    print("📁 Creating necessary directories...")
    try:
        Path("temp").mkdir(exist_ok=True)
        Path("output").mkdir(exist_ok=True)
        print("✅ Directories created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating directories: {e}")
        return False


def start_server():
    """Start the MCP server | 启动MCP服务器"""
    print("🚀 Starting Mind Map MCP Server...")
    print("   Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        subprocess.run([sys.executable, 'mind_map_server.py'])
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")


def main():
    """Main function | 主函数"""
    print_header()
    
    # Environment checks | 环境检查
    if not check_python():
        print("Please install Python 3.8 or higher and try again.")
        return
    
    if not check_node():
        print("Please install Node.js and try again.")
        return
    
    # Create directories | 创建目录
    if not create_directories():
        print("Failed to create necessary directories.")
        return
    
    # Install dependencies | 安装依赖
    print("🔧 Installing dependencies...")
    
    if not install_python_deps():
        print("Failed to install Python dependencies.")
        return
    
    if not install_node_deps():
        print("Failed to install Node.js dependencies.")
        return
    
    if not install_playwright():
        print("Failed to install browser for screenshot capture.")
        return
    
    print("✅ All dependencies installed successfully!")
    print()
    
    # Start server | 启动服务器
    start_server()


if __name__ == "__main__":
    main()