#!/usr/bin/env bash
#
# 一键启动知识库项目全部容器（应用 + 依赖），Linux / macOS。
#
# 通过项目根目录的 docker-compose.yml（include 合并 infra/ 与 app/）以「单一
# Compose 项目」方式拉起：自动共享网络（milvus / kb-net），app 可按服务名
# milvus-standalone 访问 Milvus，并由 depends_on(milvus-standalone, service_healthy) 保证
# Milvus 健康后再启动应用。无需再分两个阶段手动编排。
#
# 前置条件：
#   1. 已安装 Docker + Docker Compose v2.20+，且 Docker 正在运行；
#   2. 已存在 app/.env.prod（可从 app/.env.example 复制后填写）。
#
# 用法：
#   ./start.sh            # 构建 kb-app 并启动全部服务
#   ./start.sh --no-build # 镜像已存在时，仅启动（跳过构建）
#
set -euo pipefail

# 无论在哪调用，都切换到脚本所在的项目根目录
cd "$(dirname "$0")"

echo "==> 检查 Docker 是否运行..."
if ! docker info >/dev/null 2>&1; then
  echo "错误：Docker 未运行，请先启动 Docker Desktop / docker daemon。" >&2
  exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "错误：未找到 docker compose 插件（需 Docker Compose v2.20+，include 指令要求）。" >&2
  exit 1
fi

if [ ! -f app/.env.prod ]; then
  echo "错误：缺少 app/.env.prod。请先执行：cp app/.env.example app/.env.prod 并填写配置。" >&2
  exit 1
fi

NO_BUILD=""
if [ "${1:-}" = "--no-build" ]; then
  NO_BUILD="--no-build"
fi

echo "==> 构建并启动全部服务（根 docker-compose.yml，include 合并 infra + app）..."
docker compose up -d ${NO_BUILD}

echo "==> 等待 Milvus(milvus-standalone) 健康（最多约 240s）..."
for i in $(seq 1 40); do
  cid=$(docker compose ps -q milvus-standalone 2>/dev/null || true)
  if [ -n "$cid" ]; then
    status=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$cid" 2>/dev/null || true)
    if [ "$status" = "healthy" ]; then
      echo "    Milvus 已健康（第 ${i} 次探测）。"
      break
    fi
  fi
  if [ "$i" -eq 40 ]; then
    echo "    警告：等待 Milvus 超时，请检查：docker compose logs milvus-standalone"
  fi
  sleep 6
done

echo "==> 等待 kb-query 健康（最多约 100s）..."
for i in $(seq 1 20); do
  cid=$(docker compose ps -q kb-query 2>/dev/null || true)
  if [ -n "$cid" ]; then
    status=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$cid" 2>/dev/null || true)
    if [ "$status" = "healthy" ]; then
      echo "    kb-query 已健康（第 ${i} 次探测）。"
      break
    fi
  fi
  if [ "$i" -eq 20 ]; then
    echo "    警告：等待 kb-query 超时，请检查：docker compose logs kb-query"
  fi
  sleep 5
done

echo ""
echo "==> 启动完成。服务状态："
docker compose ps

echo ""
echo "端口映射：kb-import=8000  kb-query=8001  Milvus=19530  Attu=7000  MinIO(业务)=9000/9001"
echo "查看日志：docker compose logs -f kb-query"
echo "停止全部：docker compose down"
