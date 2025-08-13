"""
Utility Functions | 工具函数
===========================

Common utility functions used across the Mind Map MCP Server.
思维导图MCP服务器使用的通用工具函数。
"""

import subprocess
import time
from pathlib import Path
import re


def cleanup_temp_files(temp_dir: Path, max_age_hours: int = 1):
    """Clean up old temporary files | 清理旧的临时文件"""
    try:
        current_time = time.time()
        for file in temp_dir.glob("mindmap_*"):
            if current_time - file.stat().st_mtime > (max_age_hours * 3600):
                file.unlink()
                print(f"Cleaned up old temp file: {file}")
    except Exception as e:
        print(f"Error cleaning up temp files: {e}")


def fix_chinese_fonts_and_remove_watermark(html_file: Path):
    """
    Fix Chinese font rendering and remove watermark in HTML file
    修复HTML文件中的中文字体渲染并移除水印
    
    Args:
        html_file: Path to the HTML file to modify
    """
    try:
        # Read HTML content | 读取HTML内容
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Inject Chinese font support and minimal watermark removal | 注入中文字体支持和最小化水印移除
        font_css_and_watermark_removal = """
        <style>
        /* Chinese font support | 中文字体支持 */
        * {
            font-family: 'Noto Sans CJK SC', 'Microsoft YaHei', '微软雅黑', 
                         'WenQuanYi Zen Hei', '文泉驿正黑', 'SimHei', '黑体',
                         'Arial', 'Helvetica', sans-serif !important;
        }
        
        /* Improve Chinese text rendering | 改善中文文本渲染 */
        text {
            font-weight: normal;
            text-rendering: optimizeLegibility;
            letter-spacing: 0.2px;
        }
        </style>
        
        <script>
        // Conservative watermark removal after page is fully loaded | 页面完全加载后保守的水印移除
        window.addEventListener('load', function() {
            setTimeout(() => {
                // Only remove elements that are clearly watermarks | 只移除明确是水印的元素
                
                // Remove toolbar elements if they exist | 移除工具栏元素（如果存在）
                const toolbar = document.querySelector('.markmap-toolbar');
                if (toolbar) {
                    toolbar.style.display = 'none';
                }
                
                // Remove any links with markmap in href | 移除href中包含markmap的链接
                const watermarkLinks = document.querySelectorAll('a[href*="markmap"], a[href*="github.com/gera2ld"]');
                watermarkLinks.forEach(link => {
                    // Only remove if it's clearly a watermark (low opacity or specific positioning)
                    const opacity = parseFloat(link.getAttribute('opacity') || '1');
                    if (opacity <= 0.3) {
                        link.style.display = 'none';
                    }
                });
                
                // Remove SVG text elements that are watermarks | 移除SVG中的水印文本元素
                const svgTexts = document.querySelectorAll('svg text');
                svgTexts.forEach(text => {
                    const href = text.getAttribute('href') || '';
                    if (href.includes('markmap') || href.includes('github.com/gera2ld')) {
                        text.style.display = 'none';
                    }
                });
                
            }, 1000); // Wait longer to ensure everything is loaded | 等待更长时间确保所有内容加载完成
        });
        </script>
        """
        
        # Insert font CSS and watermark removal before closing head tag | 在head标签结束前插入字体CSS和水印移除
        if '</head>' in content:
            content = content.replace('</head>', font_css_and_watermark_removal + '\n</head>')
        else:
            # If no head tag, insert at the beginning | 如果没有head标签，在开头插入
            content = font_css_and_watermark_removal + '\n' + content
        
        # Remove only obvious watermark comments | 只移除明显的水印注释
        watermark_patterns = [
            r'<!--.*?markmap.*?-->',
            r'<!--.*?powered by.*?-->'
        ]
        
        for pattern in watermark_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Write modified content back | 将修改后的内容写回
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Applied Chinese font fixes to: {html_file}")
        
    except Exception as e:
        print(f"Error fixing Chinese fonts in {html_file}: {e}")


def validate_markdown_content(content: str) -> tuple[bool, str]:
    """
    Validate Markdown content for mind map generation
    验证用于思维导图生成的Markdown内容
    
    Args:
        content: Markdown content to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not content or not content.strip():
        return False, "Markdown content cannot be empty"
    
    # Check if content has at least one header | 检查内容是否至少有一个标题
    if not re.search(r'^#+\s+', content, re.MULTILINE):
        return False, "Markdown content should contain at least one header (# Title)"
    
    # Remove size limit - let the system handle large content naturally
    # 移除大小限制 - 让系统自然处理大内容
    
    return True, ""


def split_large_markdown(content: str, max_size: int = 120000) -> list[str]:
    """
    Split large Markdown content into smaller chunks | 将大型Markdown内容分割成较小的块
    
    Args:
        content: Markdown content to split
        max_size: Maximum size per chunk in characters
        
    Returns:
        list: List of content chunks
    """
    if len(content) <= max_size:
        return [content]
    
    chunks = []
    lines = content.split('\n')
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line_size = len(line) + 1  # +1 for newline
        
        # If adding this line would exceed the limit, start a new chunk
        if current_size + line_size > max_size and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_size = line_size
        else:
            current_chunk.append(line)
            current_size += line_size
    
    # Add the last chunk if it has content
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    将文件大小格式化为人类可读格式
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def get_system_info() -> dict:
    """
    Get system information for debugging
    获取用于调试的系统信息
    
    Returns:
        dict: System information
    """
    import platform
    import sys
    
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.architecture()[0],
        "python_version": sys.version,
        "python_executable": sys.executable,
        "working_directory": str(Path.cwd())
    }


def check_dependencies() -> dict:
    """
    Check if all required dependencies are available
    检查是否所有必需的依赖项都可用
    
    Returns:
        dict: Dependency check results
    """
    results = {
        "markmap_cli": False,
        "playwright": False,
        "chromium": False
    }
    
    # Check markmap-cli | 检查markmap-cli
    try:
        result = subprocess.run(['markmap', '--version'], 
                               capture_output=True, text=True, timeout=10)
        results["markmap_cli"] = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        results["markmap_cli"] = False
    
    # Check playwright | 检查playwright
    try:
        import playwright
        results["playwright"] = True
    except ImportError:
        results["playwright"] = False
    
    # Check chromium availability | 检查chromium可用性
    if results["playwright"]:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch()
                browser.close()
            results["chromium"] = True
        except Exception:
            results["chromium"] = False
    
    return results