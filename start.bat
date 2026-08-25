@echo off
setlocal EnableDelayedExpansion
REM ============================================================
REM 一键启动知识库项目全部容器（应用 + 依赖），Windows
REM
REM 通过项目根 docker-compose.yml（include 合并 infra/ 与 app/）以单一
REM Compose 项目拉起：自动共享网络（milvus / kb-net），app 按服务名
REM milvus-standalone 访问 Milvus，并由 depends_on(milvus-standalone, service_healthy)
REM 保证 Milvus 健康后再启动应用。无需再分两个阶段手动编排。
REM
REM 前置条件：
REM   1. 已安装 Docker Desktop 且正在运行（需 Docker Compose v2.20+）；
REM   2. 已存在 app\.env.prod（可从 app\.env.example 复制后填写）。
REM
REM 用法：
REM   start.bat            （构建 kb-app 并启动全部）
REM   start.bat --no-build （镜像已存在时仅启动）
REM ============================================================

cd /d "%~dp0"

echo ==^> 检查 Docker 是否运行...
docker info >nul 2>&1
if errorlevel 1 (
  echo 错误：Docker 未运行，请先启动 Docker Desktop。
  exit /b 1
)

docker compose version >nul 2>&1
if errorlevel 1 (
  echo 错误：未找到 docker compose 插件（需 Docker Compose v2.20+）。
  exit /b 1
)

if not exist app\.env.prod (
  echo 错误：缺少 app\.env.prod。请先执行：copy app\.env.example app\.env.prod 并填写配置。
  exit /b 1
)

set "NO_BUILD="
if "%~1"=="--no-build" set "NO_BUILD=--no-build"

echo ==^> 构建并启动全部服务（根 docker-compose.yml，include 合并 infra + app）...
docker compose up -d %NO_BUILD%

echo ==^> 等待 Milvus(milvus-standalone) 健康（最多约 240s）...
set /a tries=0
:wait_milvus
set "status=unknown"
for /f "usebackq tokens=*" %%c in (`docker compose ps -q milvus-standalone 2^>nul`) do (
  for /f "usebackq tokens=*" %%h in (`docker inspect -f "{{.State.Health.Status}}" %%c 2^>nul`) do set "status=%%h"
)
if "!status!"=="healthy" goto milvus_ok
set /a tries+=1
if %tries% geq 40 (
  echo    警告：等待 Milvus 超时，请检查：docker compose logs milvus-standalone
  goto milvus_ok
)
timeout /t 6 >nul
goto wait_milvus
:milvus_ok

echo ==^> 等待 kb-query 健康（最多约 100s）...
set /a tries=0
:wait_query
set "status=unknown"
for /f "usebackq tokens=*" %%c in (`docker compose ps -q kb-query 2^>nul`) do (
  for /f "usebackq tokens=*" %%h in (`docker inspect -f "{{.State.Health.Status}}" %%c 2^>nul`) do set "status=%%h"
)
if "!status!"=="healthy" goto query_ok
set /a tries+=1
if %tries% geq 20 (
  echo    警告：等待 kb-query 超时，请检查：docker compose logs kb-query
  goto query_ok
)
timeout /t 5 >nul
goto wait_query
:query_ok

echo.
echo ==^> 启动完成。服务状态：
docker compose ps

echo.
echo 端口映射：kb-import=8000  kb-query=8001  Milvus=19530  Attu=7000  MinIO(业务)=9000/9001
echo 查看日志： docker compose logs -f kb-query
echo 停止全部： docker compose down
endlocal
