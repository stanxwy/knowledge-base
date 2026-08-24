FROM python:3.11-slim

# Python 和 pip 环境配置
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PYTHONPATH=/app \
    PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10

WORKDIR /app

# 使用腾讯云 Debian 镜像源，并安装系统依赖
RUN sed -i \
        's|http://deb.debian.org/debian|http://mirrors.tencentyun.com/debian|g; \
         s|http://deb.debian.org/debian-security|http://mirrors.tencentyun.com/debian-security|g' \
        /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# 先复制依赖文件，便于复用 Docker 构建缓存
COPY requirements.txt /app/requirements.txt

# 使用阿里云镜像源升级 Python 打包工具
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade \
        pip \
        setuptools \
        wheel

# 使用阿里云镜像源安装项目依赖
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install \
        --default-timeout=300 \
        --retries=10 \
        -r /app/requirements.txt

# 复制项目代码
COPY app /app/knowledge

# 创建运行过程中使用的临时目录和日志目录
RUN mkdir -p /app/temp-files /app/logs

# 导入服务使用 8000，查询服务使用 8001
EXPOSE 8000 8001

# 默认启动查询服务
# Compose 中的 kb-import 会通过 command 覆盖此命令
CMD ["python", "-m", "uvicorn", "knowledge.api.query_router:create_app", "--factory", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]