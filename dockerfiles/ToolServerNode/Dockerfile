# 使用官方的 Python 3.10 基础镜像
FROM python:3.10

# 设置镜像标签
LABEL Role="toolserver.node"

# 暴露服务端口
EXPOSE 31942

# 设置工作目录
WORKDIR /app

# 更新包列表
RUN apt-get update

# 安装必要的软件包
RUN apt update && apt install -y build-essential make openjdk-17-jdk-headless curl docker.io docker-compose psmisc sudo

# 配置 pip 使用清华大学的镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 Playwright 及其依赖
RUN pip install playwright && playwright install chromium &&  playwright install-deps

# 复制依赖文件
COPY ToolServer/ToolServerNode/requirements.txt .

# 安装 Python 依赖包
RUN pip install --no-cache-dir -r requirements.txt

# 清理临时文件
RUN rm -rf /tmp/* /var/tmp/*

# 复制应用程序文件
COPY ToolServer/ToolServerNode .

# 创建资产目录
RUN mkdir -p assets

# 创建工作空间目录
RUN mkdir -p workspace

# 设置入口点，使用 uvicorn 运行应用程序
ENTRYPOINT [ "uvicorn", "main:app", "--host", "0.0.0.0","--port","31942" ]
