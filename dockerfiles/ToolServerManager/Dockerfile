# 使用官方的 Python 3.10 基础镜像
FROM python:3.10

# 设置镜像标签
LABEL Role="toolserver.manager"

# 暴露服务端口
EXPOSE 8080

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY ToolServer/ToolServerManager/requirements.txt .

# 安装 Python 依赖包
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序文件
COPY ToolServer/ToolServerManager .

# 创建资产目录
RUN mkdir -p assets

# 配置健康检查，检测服务是否存活
HEALTHCHECK --interval=30s --timeout=5s --start-period=1s --retries=3 CMD ["bash", "-c", "curl -sS 'http://localhost:8080/alive' || exit 1"]

# 设置入口点，使用 gunicorn 运行应用程序
ENTRYPOINT [ "gunicorn", "main:app", "-b","0.0.0.0:8080","--worker-class","uvicorn.workers.UvicornWorker"]
