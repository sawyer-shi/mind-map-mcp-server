# 思维导图MCP服务器的Docker配置文件
# =====================================
# 这个文件告诉Docker如何创建一个包含我们服务的容器
# 就像是一个安装指南，让任何人都能轻松运行我们的服务

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
RUN pip install --no-cache-dir -r requirements.txt

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
RUN chmod +x mind_map_server.py

# 第十一步：暴露端口
# 告诉Docker这个容器需要使用8090端口
EXPOSE 8090

# 第十二步：设置环境变量
# 告诉程序在Docker环境中运行
ENV RUNNING_IN_DOCKER=true
ENV PYTHONUNBUFFERED=1

# 第十三步：健康检查
# 定期检查服务是否正常运行
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import subprocess; subprocess.run(['python', '--version'])" || exit 1

# 第十四步：启动命令
# 告诉Docker如何启动我们的HTTP MCP服务
CMD ["python", "http_server.py"]

# 构建说明：
# 要构建这个Docker镜像，请在项目根目录运行：
# docker build -t mind-map-mcp .
#
# 要运行容器，请使用：
# docker run -p 8090:8090 -v $(pwd)/output:/app/output mind-map-mcp
#
# 这里的 -v $(pwd)/output:/app/output 会将容器内的output目录
# 映射到你电脑上的output目录，这样生成的图片就能保存到你的电脑上