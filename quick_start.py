#!/usr/bin/env python3
"""
Quick Start Script - Mind Map Service | 快速开始脚本 - 思维导图服务
================================================================

This script is designed for users with no programming background.
It provides the simplest way to guide you through starting the mind map service.

Just like the "one-click setup" feature on your phone - super simple!

这个脚本是为完全没有编程基础的用户准备的
它会用最简单的方式指导你启动思维导图服务

就像手机的"一键设置"功能一样简单！
"""

import os
import sys
import time
import subprocess
from pathlib import Path


def clear_screen():
    """Clear screen function | 清屏功能"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_welcome():
    """Print welcome message | 打印欢迎信息"""
    print("🎉" * 20)
    print("🧠 Welcome to Mind Map Service!")
    print("   Your personal mind map creation factory")
    print("🎉" * 20)
    print()
    print("📖 This service helps you turn text into beautiful mind maps")
    print("   It's as simple as drawing your ideas into a picture!")
    print()


def print_menu():
    """Print menu options | 打印菜单选项"""
    print("🚀 Please choose startup method:")
    print()
    print("1️⃣  Docker Start (Recommended) - Simplest, one-click solution")
    print("2️⃣  Local Start (Auto-install) - Will auto-install required components")
    print("3️⃣  View Project Information")
    print("4️⃣  View Usage Examples")
    print("0️⃣  Exit")
    print()


def docker_start():
    """Docker startup | Docker启动"""
    print("🐳 Starting service with Docker...")
    print()
    
    # Check if Docker is installed | 检查Docker是否安装
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker is not installed or not running")
            print("   Please install Docker Desktop first: https://www.docker.com/products/docker-desktop")
            return False
        print(f"✅ Docker version: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Docker is not installed")
        print("   Please install Docker Desktop first: https://www.docker.com/products/docker-desktop")
        return False
    
    print()
    print("🚢 Starting Docker container...")
    try:
        # Start docker-compose | 启动docker-compose
        result = subprocess.run(['docker-compose', 'up', '-d'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker container started successfully!")
            print()
            print("🌐 Service URLs:")
            print("   • HTTP MCP Endpoint: http://localhost:8090/mcp")
            print("   • Service Status Page: http://localhost:8090")
            print()
            print("📋 Common Commands:")
            print("   • View logs: docker-compose logs -f")
            print("   • Stop service: docker-compose down")
            return True
        else:
            print("❌ Docker startup failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error starting Docker: {e}")
        return False


def local_start():
    """Local startup (call start_server.py) | 本地启动（调用start_server.py）"""
    print("💻 Starting with local environment...")
    print("   Calling auto-install script...")
    print()
    
    try:
        subprocess.run([sys.executable, 'start_server.py'])
    except KeyboardInterrupt:
        print("\n⏹️  Startup interrupted by user")
    except Exception as e:
        print(f"❌ Startup failed: {e}")


def show_project_info():
    """Display project information | 显示项目信息"""
    clear_screen()
    print("📚 Project Information")
    print("=" * 50)
    print()
    print("📝 Project Name: Mind Map MCP Server")
    print("👨‍💻 Author: sawyer-shi")
    print("🌐 Repository: https://github.com/sawyer-shi/mind-map-mcp-server.git")
    print()
    print("✨ Main Features:")
    print("   • 📝 Convert Markdown text to mind maps")
    print("   • 🖼️ Generate high-quality PNG images")
    print("   • 🐳 Support Docker one-click deployment")
    print("   • 🔌 Full MCP protocol support")
    print("   • 🌐 Support multiple languages including Chinese")
    print()
    print("📁 Project Files:")
    print("   • mind_map_server.py - Main server (stdio mode)")
    print("   • http_server.py - HTTP server")
    print("   • start_server.py - Auto-install script")
    print("   • examples/ - Usage examples")
    print("   • temp/ - Temporary files directory")
    print("   • output/ - Generated images directory")
    print()
    input("Press Enter to return to main menu...")


def show_examples():
    """Display usage examples | 显示使用示例"""
    clear_screen()
    print("📋 Usage Examples")
    print("=" * 50)
    print()
    print("🎯 Input Example (Markdown format):")
    print()
    print("```markdown")
    print("# My Learning Plan")
    print()
    print("## Programming")
    print("### Frontend Development")
    print("- HTML Basics")
    print("- CSS Styling")  
    print("- JavaScript")
    print()
    print("### Backend Development")
    print("- Python")
    print("- Databases")
    print()
    print("## Project Practice")
    print("### Personal Projects")
    print("- Personal Blog")
    print("- Todo Application")
    print("```")
    print()
    print("🖼️ Output Result:")
    print("   The system will generate a beautiful mind map PNG image")
    print("   Images will be saved in the output/ directory")
    print()
    print("📂 More examples available at:")
    print("   • examples/sample_mindmap.md - Basic example")
    print("   • examples/company_structure.md - Company structure chart")
    print("   • examples/how_to_use.md - Detailed usage instructions")
    print()
    input("Press Enter to return to main menu...")


def main():
    """Main function | 主函数"""
    while True:
        clear_screen()
        print_welcome()
        print_menu()
        
        try:
            choice = input("Please enter your choice (0-4): ").strip()
            
            if choice == '1':
                clear_screen()
                docker_start()
                input("\nPress Enter to return to main menu...")
                
            elif choice == '2':
                clear_screen()
                local_start()
                input("\nPress Enter to return to main menu...")
                
            elif choice == '3':
                show_project_info()
                
            elif choice == '4':
                show_examples()
                
            elif choice == '0':
                print("\n👋 Thank you for using, goodbye!")
                break
                
            else:
                print("❌ Please enter a valid option (0-4)")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n👋 Program interrupted, goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()