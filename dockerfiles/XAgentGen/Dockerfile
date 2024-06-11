# 使用 PyTorch 2.1.0 带 CUDA 11.8 和 cuDNN 8 的开发镜像
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-devel

# 设置镜像标签
LABEL Role="xagentgen.node"

# 设置工作目录
WORKDIR /app

# 更新包列表并安装必要的软件包
RUN apt update && apt install -y git ninja-build

# 配置 pip 使用清华大学的镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装必要的 Python 包
RUN pip install --no-cache-dir packaging

# 安装 flash-attn 包，限制最大并行作业数为 8
RUN MAX_JOBS=8 pip install flash-attn==2.0.4 --no-build-isolation

# 安装 vllm 包
RUN pip install --no-cache-dir https://github.com/vllm-project/vllm/releases/download/v0.2.2/vllm-0.2.2+cu118-cp310-cp310-manylinux1_x86_64.whl

# 安装 xformers 包，使用 PyTorch 官方的索引 URL
RUN pip install --no-cache-dir -U xformers --index-url https://download.pytorch.org/whl/cu118

# 复制并安装应用程序的依赖
COPY XAgentGen/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装特定版本的 pydantic 包
RUN pip install --no-cache-dir pydantic==1.10.13

# 清理临时文件
RUN rm -rf /tmp/* /var/tmp/*

# 复制应用程序文件
COPY XAgentGen .
