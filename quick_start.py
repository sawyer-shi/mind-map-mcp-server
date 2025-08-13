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
import shutil

# Load environment variables if available | 如果可用，加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, will use system environment variables
    # python-dotenv未安装，将使用系统环境变量
    pass


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
    print("1️⃣  Docker Start (All Transports) - Full multi-transport support")
    print("2️⃣  Docker Start (Streamable HTTP) - Web transport only")
    print("3️⃣  Local Start - Choose specific transport protocol")  
    print("4️⃣  Docker Start (Single Transport) - Choose specific transport")
    print("5️⃣  View Project Information")
    print("6️⃣  View Usage Examples")
    print("7️⃣  View Transport Protocol Guide")
    print("8️⃣  Configuration Management - Setup .env file")
    print("0️⃣  Exit")
    print()


def docker_start_all_transports():
    """Docker startup with all transports | Docker启动（所有传输方式）"""
    print("🐳 Starting all MCP transport services with Docker...")
    print("   Including stdio and streamable-http protocols")
    print()
    
    # Check if Docker is installed | 检查Docker是否安装
    if not _check_docker():
        return False
    
    print()
    print("🚢 Starting all transport services...")
    try:
        # Start all services including stdio | 启动包括stdio在内的所有服务
        result = subprocess.run(['docker-compose', '--profile', 'stdio', 'up', '-d'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ All transport services started successfully!")
            print()
            print("🌐 Service Endpoints:")
            print("   • Stdio Transport: Interactive command-line interface")
            print("   • Streamable HTTP: http://localhost:8091/mcp")  
            print()
            print("📋 Common Commands:")
            print("   • Test stdio interactively: docker-compose --profile stdio run --rm mind-map-stdio")
            print("   • View HTTP logs: docker-compose logs -f mind-map-streamable")
            print("   • View stdio logs: docker-compose --profile stdio logs -f mind-map-stdio")
            print("   • Stop all services: docker-compose --profile stdio down")
            return True
        else:
            print("❌ Docker startup failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error starting Docker: {e}")
        return False


def docker_start_web_only():
    """Docker startup with web transports only | Docker启动（仅Web传输方式）"""
    print("🐳 Starting web-based MCP transport services with Docker...")
    print("   Streamable HTTP protocol only")
    print()
    
    # Check if Docker is installed | 检查Docker是否安装
    if not _check_docker():
        return False
    
    print()
    print("🚢 Starting web transport services...")
    try:
        # Start unified docker-compose | 启动统一docker-compose
        result = subprocess.run(['docker-compose', 'up', '-d'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Web transport services started successfully!")
            print()
            print("🌐 Service URLs:")
            print("   • MCP Server: http://localhost:8091/mcp")  
            print("   • Static Files: http://localhost:8090/output")
            print()
            print("📋 Common Commands:")
            print("   • View MCP logs: docker-compose logs -f mind-map-streamable")
            print("   • View static server logs: docker-compose logs -f mind-map-static")
            print("   • Stop services: docker-compose down")
            return True
        else:
            print("❌ Docker startup failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error starting Docker: {e}")
        return False


def docker_start_single():
    """Docker startup with single transport | Docker启动（单一传输方式）"""    
    transport = _choose_transport()
    if not transport:
        return False
        
    print(f"🐳 Starting {transport.upper()} transport service with Docker...")
    print()
    
    if not _check_docker():
        return False
    
    service_name = f"mind-map-{transport}"
    endpoint_map = {
        "stdio": "Interactive command-line interface",
        "streamable": "http://localhost:8091/mcp"
    }
    
    print()
    print(f"🚢 Starting {transport} service...")
    try:
        if transport == 'stdio':
            # Stdio requires profile flag | stdio需要profile标志
            result = subprocess.run(['docker-compose', '--profile', 'stdio', 'up', '-d', service_name], 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(['docker-compose', 'up', '-d', service_name], 
                                  capture_output=True, text=True)
                                  
        if result.returncode == 0:
            print(f"✅ {transport.upper()} service started successfully!")
            print()
            print("🌐 Service Endpoint:")
            print(f"   • {transport.upper()}: {endpoint_map[transport]}")
            print()
            print("📋 Commands:")
            if transport == 'stdio':
                print(f"   • Test interactively: docker-compose --profile stdio run --rm {service_name}")
                print(f"   • View logs: docker-compose --profile stdio logs -f {service_name}")
                print(f"   • Stop service: docker-compose --profile stdio stop {service_name}")
            else:
                print(f"   • View logs: docker-compose logs -f {service_name}")
                print(f"   • Stop service: docker-compose stop {service_name}")
            return True
        else:
            print("❌ Docker startup failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error starting Docker: {e}")
        return False


def _check_docker():
    """Check if Docker is installed | 检查Docker是否安装"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker is not installed or not running")
            print("   Please install Docker Desktop first: https://www.docker.com/products/docker-desktop")
            return False
        print(f"✅ Docker version: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ Docker is not installed")
        print("   Please install Docker Desktop first: https://www.docker.com/products/docker-desktop")
        return False


def _choose_transport():
    """Choose MCP transport protocol | 选择MCP传输协议"""
    print("🔌 Choose MCP Transport Protocol:")
    print()
    print("1️⃣  stdio - Standard I/O (for local tools and command-line)")
    print("2️⃣  streamable-http - Streamable HTTP (modern web standard)")
    print("0️⃣  Back to main menu")
    print()
    
    while True:
        choice = input("Please choose transport (1-2, 0 to go back): ").strip()
        
        if choice == '1':
            return 'stdio'
        elif choice == '2':
            return 'streamable'
        elif choice == '0':
            return None
        else:
            print("❌ Please enter a valid option (1-2, 0 to go back)")


def local_start_with_transport():
    """Local startup with transport selection | 本地启动（选择传输方式）"""
    transport = _choose_transport()
    if not transport:
        return
    
    print(f"💻 Starting {transport.upper()} transport locally...")
    print("   This will auto-install required components...")
    print()
    
    try:
        if transport == 'stdio':
            subprocess.run([sys.executable, 'main.py', 'stdio'])
        elif transport == 'streamable':
            subprocess.run([sys.executable, 'main.py', 'streamable-http'])
    except KeyboardInterrupt:
        print(f"\n⏹️  {transport.upper()} server stopped by user")
    except Exception as e:
        print(f"❌ Server startup failed: {e}")


def show_transport_guide():
    """Display transport protocol guide | 显示传输协议指南"""
    clear_screen()
    print("🔌 MCP Transport Protocol Guide")
    print("=" * 50)
    print()
    
    print("📺 Stdio (Standard Input/Output)")
    print("   • Best for: Local tools, command-line applications")
    print("   • Usage: Direct process communication via stdin/stdout")
    print("   • Endpoint: Interactive command-line interface")
    print("   • Pros: Simple, reliable, perfect for local tools")
    print("   • Cons: Not suitable for web applications")
    print()
    
    print("🚀 Streamable HTTP")
    print("   • Best for: Modern web applications, full-duplex communication")
    print("   • Usage: Bidirectional streaming over HTTP")
    print("   • Endpoint: http://localhost:8091/mcp")
    print("   • Pros: Full MCP protocol support, modern standard")
    print("   • Cons: Newer protocol, requires compatible clients")
    print()
    
    print("💡 Recommendations:")
    print("   • Use Stdio for local tools, CLIs, development environments")
    print("   • Use Streamable HTTP for production web applications (recommended)")
    print("   • Both protocols support the same MCP tools and resources")
    print()
    
    print("🔗 Client Connection Examples:")
    print("   • CherryStudio: Direct stdio connection")
    print("   • Dify: Use mcp-remote proxy with web endpoints")
    print("   • Custom clients: Connect directly to the endpoints above")
    print()
    
    input("Press Enter to return to main menu...")


def manage_configuration():
    """Configuration management interface | 配置管理界面"""
    clear_screen()
    print("⚙️ Configuration Management")
    print("=" * 50)
    print()
    
    env_file = Path(".env")
    template_file = Path("env.template")
    
    # Check if files exist | 检查文件是否存在
    env_exists = env_file.exists()
    template_exists = template_file.exists()
    
    print("📄 Configuration Files Status:")
    print(f"   .env file: {'✅ EXISTS' if env_exists else '❌ NOT FOUND'}")
    print(f"   env.template: {'✅ EXISTS' if template_exists else '❌ NOT FOUND'}")
    print()
    
    if not template_exists:
        print("❌ env.template file not found!")
        print("   This file should contain the configuration template.")
        input("Press Enter to return to main menu...")
        return
    
    print("🔧 Configuration Options:")
    print("1️⃣  Create .env from template (if not exists)")
    print("2️⃣  View current .env configuration") 
    print("3️⃣  Reset .env to template defaults")
    print("4️⃣  Show current environment values")
    print("0️⃣  Back to main menu")
    print()
    
    while True:
        choice = input("Please choose option (1-4, 0 to go back): ").strip()
        
        if choice == '1':
            create_env_from_template(env_file, template_file, env_exists)
            break
        elif choice == '2':
            view_env_configuration(env_file)
            break
        elif choice == '3':
            reset_env_to_template(env_file, template_file)
            break
        elif choice == '4':
            show_current_config()
            break
        elif choice == '0':
            return
        else:
            print("❌ Please enter a valid option (1-4, 0 to go back)")


def create_env_from_template(env_file, template_file, env_exists):
    """Create .env file from template | 从模板创建.env文件"""
    if env_exists:
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite not in ['y', 'yes']:
            print("Operation cancelled.")
            input("Press Enter to continue...")
            return
    
    try:
        shutil.copy2(template_file, env_file)
        print("✅ .env file created successfully from template!")
        print()
        print("📝 Next steps:")
        print("   1. Edit the .env file with your preferred settings")  
        print("   2. Customize ports, host, and debug settings")
        print("   3. Save the file and restart services")
        print()
        print("💡 Tip: Use any text editor to modify the .env file")
        print(f"   File location: {env_file.absolute()}")
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
    
    input("\nPress Enter to continue...")


def view_env_configuration(env_file):
    """View current .env configuration | 查看当前.env配置"""
    if not env_file.exists():
        print("❌ .env file not found!")
        print("   Use option 1 to create it from template.")
        input("Press Enter to continue...")
        return
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("📄 Current .env Configuration:")
        print("=" * 40)
        print(content)
        print("=" * 40)
        
    except Exception as e:
        print(f"❌ Failed to read .env file: {e}")
    
    input("\nPress Enter to continue...")


def reset_env_to_template(env_file, template_file):
    """Reset .env to template defaults | 重置.env为模板默认值"""
    print("⚠️  This will overwrite your current .env file!")
    confirm = input("Are you sure? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Operation cancelled.")
        input("Press Enter to continue...")
        return
    
    try:
        shutil.copy2(template_file, env_file)
        print("✅ .env file reset to template defaults!")
        print("   You can now edit it with your custom settings.")
        
    except Exception as e:
        print(f"❌ Failed to reset .env file: {e}")
    
    input("Press Enter to continue...")


def show_current_config():
    """Show current effective configuration | 显示当前有效配置"""
    print("🔍 Current Environment Configuration:")
    print("=" * 40)
    
    # Define configuration keys to check | 定义要检查的配置键
    config_keys = [
        ('HOST', '0.0.0.0'),
        ('LOCAL_HOST', '127.0.0.1'),
        ('STREAMABLE_PORT', '8091'),
        ('DEBUG', 'false'),
        ('LOG_LEVEL', 'INFO'),
        ('HOST_TEMP_PATH', './temp'),
        ('HOST_OUTPUT_PATH', './output'),
        ('HOST_LOG_PATH', './logs'),
    ]
    
    for key, default in config_keys:
        value = os.getenv(key, default)
        print(f"   {key}: {value}")
    
    print("=" * 40)
    print()
    print("💡 These values come from:")
    print("   1. .env file (if exists)")
    print("   2. System environment variables") 
    print("   3. Default values (if not set)")
    
    input("\nPress Enter to continue...")


# Update the original docker_start for backward compatibility
def docker_start():
    """Docker startup (backward compatibility) | Docker启动（向后兼容）"""
    return docker_start_all()


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
    print("   • 🖼️ Generate high-quality PNG images (watermark-free)")
    print("   • ☁️ Multi-cloud storage support (Local, Aliyun OSS, AWS S3, Azure, GCS, etc.)")
    print("   • 🔍 Smart image listing by date and name filtering")
    print("   • 🐳 Support Docker one-click deployment (RECOMMENDED)")
    print("   • 🔌 Full MCP protocol support with optimized responses")
    print("   • 🌐 Support multiple languages including Chinese")
    print("   • ✅ Advanced image validation and error handling")
    print()
    print("📁 Project Files:")
    print("   • main.py - Main entry point (modular architecture)")
    print("   • src/ - Source code modules")
    print("   •   ├── server.py - Main server class")
    print("   •   ├── mind_map_generator.py - Mind map generation logic")
    print("   •   ├── mcp_tools.py - MCP tool definitions (create_mind_map, list_images)")
    print("   •   ├── storage_manager.py - Multi-cloud storage management")
    print("   •   ├── config.py - Configuration management")
    print("   •   └── utils.py - Utility functions")
    print("   • static_server.py - Static file serving for generated images")
    print("   • start_server.py - Auto-install startup script")
    print("   • quick_start.py - User-friendly startup interface")
    print("   • docker-compose.yml - Docker orchestration (2 services)")
    print("   • examples/ - Usage examples and documentation")
    print("   • temp/ - Temporary files directory")
    print("   • output/ - Generated images directory (organized by date)")
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
            choice = input("Please enter your choice (0-8): ").strip()
            
            if choice == '1':
                clear_screen()
                docker_start_all_transports()
                input("\nPress Enter to return to main menu...")
                
            elif choice == '2':
                clear_screen()
                docker_start_web_only()
                input("\nPress Enter to return to main menu...")
                
            elif choice == '3':
                clear_screen()
                local_start_with_transport()
                input("\nPress Enter to return to main menu...")
                
            elif choice == '4':
                clear_screen()
                docker_start_single()
                input("\nPress Enter to return to main menu...")
                
            elif choice == '5':
                show_project_info()
                
            elif choice == '6':
                show_examples()
                
            elif choice == '7':
                show_transport_guide()
                
            elif choice == '8':
                manage_configuration()
                
            elif choice == '0':
                print("\n👋 Thank you for using, goodbye!")
                break
                
            else:
                print("❌ Please enter a valid option (0-8)")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n👋 Program interrupted, goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
