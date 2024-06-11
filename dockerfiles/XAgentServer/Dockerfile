# 使用 Node.js LTS 版本的 Alpine 镜像构建前端应用
FROM node:lts-alpine AS XAgentWeb

# 暴露服务端口
EXPOSE 5173

# 设置工作目录
WORKDIR /app

# 复制 package.json 文件并安装依赖
COPY XAgentWeb/package.json ./
RUN npm config set registry https://registry.npmmirror.com/ && npm install

# 复制应用代码并构建
COPY XAgentWeb .
RUN npm run build

# 使用 Python 3.10 镜像构建后端服务
FROM python:3.10 AS XAgentServer

# 暴露服务端口
EXPOSE 8090

# 更新包列表并安装必要的软件包
RUN apt-get update
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN apt-get update --fix-missing
RUN apt-get install -y nginx systemctl

# 设置工作目录
WORKDIR /app

# 复制前端构建结果到工作目录
COPY --from=XAgentWeb /app/dist ./dist/

# 复制 Nginx 配置文件
COPY XAgentServer/nginx/nginx.conf /etc/nginx/nginx.conf

# 复制并安装 Python 依赖
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY XAgentServer /app/XAgentServer
COPY XAgent /app/XAgent
COPY command.py /app/command.py
COPY command_input.py /app/command_input.py
COPY start_server.py /app/start_server.py
COPY run.py /app/run.py
COPY setup.py /app/setup.py

# 清理临时文件
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 启动 Nginx
RUN systemctl start nginx

# 设置入口点，运行 Python 应用程序
ENTRYPOINT [ "python", "start_server.py" ]
