"""
Mind Map Generator | 思维导图生成器
===================================

Core mind map generation functionality.
核心思维导图生成功能。
"""

import base64
import subprocess
import time
from pathlib import Path
from playwright.async_api import async_playwright

from utils import cleanup_temp_files, fix_chinese_fonts_and_remove_watermark
from storage_manager import StorageManager


class MindMapGenerator:
    """
    Mind Map Generator Class | 思维导图生成器类
    
    Responsible for converting Markdown content to mind map images.
    负责将Markdown内容转换为思维导图图片。
    """
    
    def __init__(self, temp_dir: Path, output_dir: Path):
        self.temp_dir = temp_dir
        self.output_dir = output_dir
        
        # Create directories if they don't exist | 如果目录不存在则创建
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize storage manager | 初始化存储管理器
        self.storage_manager = StorageManager(output_dir)
    
    async def generate_mind_map(self, markdown_content: str, title: str = "Mind Map") -> dict:
        """
        Generate mind map from Markdown content | 从Markdown内容生成思维导图
        
        Returns:
            dict: Generation result with success status and image data
        """
        try:
            print(f"Starting mind map generation: {title}")
            
            # Clean up old temporary files | 清理旧的临时文件
            cleanup_temp_files(self.temp_dir)
            
            # Generate unique filename | 生成唯一文件名
            timestamp = int(time.time())
            temp_md_file = self.temp_dir / f"mindmap_{timestamp}.md"
            temp_html_file = self.temp_dir / f"mindmap_{timestamp}.html"
            temp_png_file = self.temp_dir / f"mindmap_{timestamp}.png"
            
            # Write Markdown content to temporary file | 将Markdown内容写入临时文件
            with open(temp_md_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # Generate HTML using markmap-cli | 使用markmap-cli生成HTML
            print("Converting Markdown to HTML mind map...")
            result = subprocess.run([
                'markmap', str(temp_md_file), '--no-open', '-o', str(temp_html_file)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Markmap error: {result.stderr}")
                return {
                    "success": False,
                    "error": f"Failed to generate HTML: {result.stderr}",
                    "image_data": None
                }
            
            # Fix Chinese fonts and remove watermark | 修复中文字体并移除水印
            fix_chinese_fonts_and_remove_watermark(temp_html_file)
            
            # Convert HTML to PNG using Playwright | 使用Playwright将HTML转换为PNG
            print("Converting HTML to PNG...")
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Set viewport for better rendering | 设置视口以获得更好的渲染效果
                await page.set_viewport_size({"width": 1200, "height": 800})
                
                # Load HTML file | 加载HTML文件
                await page.goto(f'file://{temp_html_file.absolute()}')
                
                # Wait for content to load | 等待内容加载
                await page.wait_for_timeout(3000)
                
                # Remove watermarks after page is fully loaded | 页面完全加载后移除水印
                await page.evaluate("""
                    // Function to remove watermarks comprehensively | 全面移除水印的函数
                    function removeWatermarks() {
                        // Remove toolbar and brand elements | 移除工具栏和品牌元素
                        const toolbarSelectors = [
                            '.markmap-toolbar',
                            '.mm-toolbar', 
                            '.markmap-brand',
                            '.mm-brand',
                            '[class*="toolbar"]',
                            '[class*="brand"]'
                        ];
                        
                        toolbarSelectors.forEach(selector => {
                            document.querySelectorAll(selector).forEach(el => el.remove());
                        });
                        
                        // Remove all links regardless of opacity | 移除所有相关链接，不管透明度
                        document.querySelectorAll('a').forEach(link => {
                            const href = link.getAttribute('href') || '';
                            const textContent = link.textContent || '';
                            
                            // Remove if href contains markmap or github, or if it's a low opacity link
                            if (href.includes('markmap') || 
                                href.includes('github.com/gera2ld') ||
                                textContent.toLowerCase().includes('markmap') ||
                                parseFloat(link.getAttribute('opacity') || '1') < 0.8) {
                                link.remove();
                            }
                        });
                        
                        // Remove text elements with watermark links | 移除带有水印链接的文本元素
                        document.querySelectorAll('text').forEach(text => {
                            const href = text.getAttribute('href') || '';
                            const textContent = text.textContent || '';
                            
                            if (href.includes('markmap') || 
                                href.includes('github.com/gera2ld') ||
                                textContent.toLowerCase().includes('markmap')) {
                                text.remove();
                            }
                        });
                        
                        // Remove any g elements that might contain watermarks | 移除可能包含水印的g元素
                        document.querySelectorAll('g').forEach(g => {
                            const links = g.querySelectorAll('a');
                            const texts = g.querySelectorAll('text');
                            
                            // If this g element only contains watermark links/texts, remove it
                            if (links.length > 0 || texts.length > 0) {
                                let hasWatermark = false;
                                
                                links.forEach(link => {
                                    const href = link.getAttribute('href') || '';
                                    if (href.includes('markmap') || href.includes('github.com/gera2ld')) {
                                        hasWatermark = true;
                                    }
                                });
                                
                                texts.forEach(text => {
                                    const href = text.getAttribute('href') || '';
                                    if (href.includes('markmap') || href.includes('github.com/gera2ld')) {
                                        hasWatermark = true;
                                    }
                                });
                                
                                if (hasWatermark && links.length + texts.length === g.children.length) {
                                    g.remove();
                                }
                            }
                        });
                        
                        // Remove any remaining elements with markmap-related attributes | 移除任何剩余的markmap相关属性元素
                        document.querySelectorAll('[*|href*="markmap"], [*|href*="github.com/gera2ld"]').forEach(el => {
                            el.remove();
                        });
                        
                        console.log('Watermark removal completed');
                    }
                    
                    // Run watermark removal
                    removeWatermarks();
                    
                    // Run again after a short delay to catch any dynamically added elements
                    setTimeout(removeWatermarks, 500);
                """)
                
                # Wait a bit more for DOM changes to take effect | 等待DOM变化生效
                await page.wait_for_timeout(1000)
                
                # Final watermark check and removal before screenshot | 截图前最后的水印检查和移除
                await page.evaluate("""
                    // Final cleanup - remove any remaining watermark elements
                    const finalCleanup = () => {
                        // Remove any elements with low opacity that might be watermarks
                        document.querySelectorAll('[opacity]').forEach(el => {
                            const opacity = parseFloat(el.getAttribute('opacity'));
                            if (opacity < 0.5) {
                                const parent = el.parentElement;
                                if (parent && parent.tagName.toLowerCase() === 'g') {
                                    // Check if parent g only contains this low-opacity element
                                    if (parent.children.length === 1) {
                                        parent.remove();
                                    } else {
                                        el.remove();
                                    }
                                } else {
                                    el.remove();
                                }
                            }
                        });
                        
                        // Remove any remaining a tags in SVG
                        document.querySelectorAll('svg a').forEach(link => {
                            link.remove();
                        });
                        
                        console.log('Final watermark cleanup completed');
                    };
                    
                    finalCleanup();
                """)
                
                # Take screenshot | 截图
                await page.screenshot(
                    path=str(temp_png_file),
                    full_page=True,
                    type='png'
                )
                
                await browser.close()
            
            # Ensure PNG file is completely written and validate it | 确保PNG文件完全写入并验证
            import asyncio
            await asyncio.sleep(0.5)  # Wait for file write to complete | 等待文件写入完成
            
            # Verify file exists and has content | 验证文件存在且有内容
            if not temp_png_file.exists():
                raise Exception("PNG file was not created")
            
            file_size = temp_png_file.stat().st_size
            if file_size < 1000:  # PNG files should be at least 1KB | PNG文件至少应该1KB
                raise Exception(f"PNG file too small ({file_size} bytes), may be corrupted")
            
            print(f"PNG file validated: {temp_png_file} ({file_size} bytes)")
            
            # Read PNG file and encode to base64 with proper data URI format | 读取PNG文件并编码为带有正确数据URI格式的base64
            with open(temp_png_file, 'rb') as f:
                image_bytes = f.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                # Add data URI prefix for proper display in browsers and clients | 添加数据URI前缀以便在浏览器和客户端正确显示
                image_data = f"data:image/png;base64,{image_base64}"
            
            print(f"Mind map generated successfully: {temp_png_file}")
            
            # Upload to configured storage | 上传到配置的存储
            storage_result = await self.storage_manager.save_mind_map(str(temp_png_file), title)
            
            return {
                "success": True,
                "error": None,
                "image_data": image_data,
                "storage_url": storage_result.get("url"),
                "storage_message": storage_result.get("message"),
                "storage_type": storage_result.get("storage_type"),
                "temp_files": {
                    "md": str(temp_md_file),
                    "html": str(temp_html_file),
                    "png": str(temp_png_file)
                }
            }
            
        except Exception as e:
            print(f"Error generating mind map: {e}")
            return {
                "success": False,
                "error": str(e),
                "image_data": None
            }
    
