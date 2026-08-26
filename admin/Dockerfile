FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 系统依赖(用于 PG 驱动 + 文档解析)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# 先装依赖(利用 Docker 层缓存)
COPY pyproject.toml ./
RUN pip install -e .

# 其余源码
COPY . ./

# 前端构建产物挂载点(可选)
RUN mkdir -p /app/admin/static/dist

EXPOSE 8002

# 默认入口;docker-compose 中可用 command 覆盖
CMD ["uvicorn", "admin.main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "1"]