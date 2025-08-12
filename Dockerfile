# Multi-transport Mind Map MCP Server | 多传输思维导图MCP服务器
# ================================================================
# This Docker image supports two MCP transport protocols:
# - stdio: For local tools and IDEs
# - streamablehttp: For modern web applications with streaming HTTP
#
# 该Docker镜像支持两种MCP传输协议：
# - stdio: 用于本地工具和IDE
# - streamablehttp: 用于现代Web应用程序（流式HTTP）

# 第一步：选择基础环境
# 我们使用包含Python和Node.js的镜像，这样就不用分别安装了
FROM python:3.11-slim

# 第二步：设置工作目录
# 在容器内创建一个专门的文件夹来存放我们的代码
WORKDIR /app

# 第三步：安装系统依赖
# 更新软件包列表并安装必要的系统工具
RUN apt-get update && apt-get install -y \
    # Node.js和npm - 用来运行markmap-cli
    nodejs \
    npm \
    # 中文字体支持 - 解决中文乱码问题
    fonts-noto-cjk \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    # 浏览器依赖 - Playwright需要这些来运行浏览器
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libgbm1 \
    libasound2 \
    # 清理缓存，减少镜像大小
    && rm -rf /var/lib/apt/lists/*

# 第四步：复制依赖文件
# 先复制依赖文件，这样可以利用Docker的缓存机制
COPY requirements.txt ./

# 第五步：安装Python依赖
# 使用官方PyPI源
# RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# RUN pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
RUN pip install --no-cache-dir --timeout 300 --retries 3 -r requirements.txt

# 第六步：安装Node.js依赖
RUN npm install -g markmap-cli

# 第七步：安装Playwright浏览器
# 这会下载Chromium浏览器，用来将HTML转换为PNG
RUN playwright install chromium
RUN playwright install-deps chromium

# 第八步：复制项目代码
COPY . .

# 第九步：创建必要的目录
# 创建临时文件和输出文件的目录
RUN mkdir -p temp output examples

# 第十步：设置权限
# 确保服务有权限创建和修改文件
RUN chmod +x main.py

# 第十一步：暴露端口
# 告诉Docker这个容器需要使用的端口
# 8000: FastMCP default port | FastMCP默认端口
EXPOSE 8000

# 第十二步：设置环境变量
# 告诉程序在Docker环境中运行
ENV RUNNING_IN_DOCKER=true
ENV PYTHONUNBUFFERED=1

# 第十三步：健康检查
# 定期检查服务是否正常运行
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import subprocess; subprocess.run(['python', '--version'])" || exit 1

# 第十四步：启动命令
# Default command runs stdio mode | 默认命令运行stdio模式
# Can be overridden via docker run command | 可通过docker run命令覆盖
CMD ["python", "main.py", "stdio"]

# 构建和运行说明 | Build and Run Instructions:
# ==============================================
#
# 构建镜像 | Build image:
# docker build -t mind-map-mcp-unified .
#
# 运行不同传输模式 | Run different transport modes:
#
# 1. stdio模式 | stdio mode:
# docker run -it --rm -v $(pwd)/output:/app/output mind-map-mcp-unified
#
# 2. Streamable HTTP模式 | Streamable HTTP mode:
# docker run -p 8091:8091 -v $(pwd)/output:/app/output mind-map-mcp-unified python main.py streamable-http --host 0.0.0.0
#
# 映射说明 | Volume mapping:
# -v $(pwd)/output:/app/output 将生成的图片保存到本地output目录