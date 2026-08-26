@echo off
setlocal
REM ============================================================
REM Local one-click startup (Windows, no Docker)
REM Each component runs in its own window (Ctrl+C stops it):
REM   1) app (core RAG)      -> uvicorn app.main:app      :8001
REM   2) admin-frontend build (npm install + build, only if dist/ missing)
REM   3) admin (backend)      -> uvicorn admin.main:app    :8002
REM   4) admin-frontend dev   -> vite                     :5173
REM
REM Notes:
REM   - Milvus/Mongo/MinIO run on the remote VM (192.168.222.8) Docker;
REM     connection strings live in app/.env.
REM   - admin depends on a local Postgres(:5432) (admin/.env DATABASE_URL ->
REM     localhost:5432). Start local PG or forward VM:5432 to localhost:5432.
REM   - admin backend does NOT yet serve the built SPA, so the UI runs via
REM     the vite dev server (:5173) which proxies /api and /admin to :8002.
REM
REM Usage:
REM   dev-start.bat                 normal start (frontend built only if missing)
REM   dev-start.bat --no-build      skip frontend build even if dist missing
REM   dev-start.bat --force-build   force rebuild frontend
REM   dev-start.bat --migrate       run alembic upgrade head + create superuser first
REM   dev-start.bat --reload        enable --reload on both backends
REM ============================================================

cd /d "%~dp0"

REM ---------- parse args ----------
set "NO_BUILD="
set "FORCE_BUILD="
set "MIGRATE="
set "RELOAD="
for %%a in (%*) do (
  if /i "%%a"=="--no-build"     set "NO_BUILD=1"
  if /i "%%a"=="--force-build"  set "FORCE_BUILD=1"
  if /i "%%a"=="--migrate"      set "MIGRATE=1"
  if /i "%%a"=="--reload"       set "RELOAD=--reload"
)

REM ---------- env file precheck ----------
if not exist app\.env (
  echo ERROR: missing app\.env. Copy app\.env.example to app\.env and fill config.
  exit /b 1
)
if not exist admin\.env (
  echo ERROR: missing admin\.env. Copy admin\.env.example to admin\.env and fill
  echo        DATABASE_URL / DATABASE_SYNC_URL / JWT_SECRET / RAG_BASE_URL etc.
  exit /b 1
)

REM ---------- python launcher: prefer venv, fallback to uv ----------
set "APP_PY=app\.venv\Scripts\python.exe"
if not exist "%APP_PY%" (
  where uv >nul 2>&1 && set "APP_PY=uv run --project app -- python"
)
set "ADMIN_PY=admin\.venv\Scripts\python.exe"
if not exist "%ADMIN_PY%" (
  where uv >nul 2>&1 && set "ADMIN_PY=uv run --project admin -- python"
)
if not exist "%APP_PY%" (
  echo ERROR: no Python env for app. Create app\.venv or install uv.
  exit /b 1
)
if not exist "%ADMIN_PY%" (
  echo ERROR: no Python env for admin. Create admin\.venv or install uv.
  exit /b 1
)

REM ---------- node/npm precheck ----------
where node >nul 2>&1
if errorlevel 1 (
  echo ERROR: node not found. Install Node.js ^(20+ recommended^).
  exit /b 1
)
where npm >nul 2>&1
if errorlevel 1 (
  echo ERROR: npm not found ^(ships with Node.js^). Check your Node install.
  exit /b 1
)

REM ---------- precheck: local Postgres(:5432) reachable (admin dep) ----------
powershell -NoProfile -Command "try { (Test-NetConnection -ComputerName localhost -Port 5432 -InformationLevel Quiet) } catch { $false }" 2>nul | findstr /i "True" >nul
if errorlevel 1 (
  echo WARNING: local Postgres^(:5432^) not reachable; admin DB ops will fail.
  echo          Start local Postgres or forward VM:5432 to localhost:5432.
) else (
  echo Precheck: local Postgres^(:5432^) reachable.
)

echo.
echo ==^> [1/4] Starting core RAG service app  (http://localhost:8001) ...
start "kb-app  (RAG API :8001)" cmd /k "%APP_PY% -m uvicorn app.main:app --host 0.0.0.0 --port 8001 %RELOAD%"

echo ==^> [2/4] Building admin frontend (admin-frontend) ...
set "DO_BUILD=0"
if not exist admin-frontend\dist\index.html set "DO_BUILD=1"
if defined FORCE_BUILD set "DO_BUILD=1"
if defined NO_BUILD set "DO_BUILD=0"

if "%DO_BUILD%"=="1" (
  echo     Running npm install + npm run build ...
  pushd admin-frontend
  call npm install
  if errorlevel 1 (
    echo     ERROR: npm install failed. Check network / Node version.
    popd
    exit /b 1
  )
  call npm run build
  if errorlevel 1 (
    echo     ERROR: npm run build failed.
    popd
    exit /b 1
  )
  popd
  echo     Frontend built -> admin-frontend\dist
) else (
  echo     Already built ^(admin-frontend\dist exists^); skipped.
)

echo ==^> [3/4] Starting admin backend  (http://localhost:8002) ...
if defined MIGRATE (
  echo     Running DB migration: alembic upgrade head ...
  %ADMIN_PY% -m alembic upgrade head
  echo     Ensuring superuser ^(admin.scripts.create_superuser^) ...
  %ADMIN_PY% -m admin.scripts.create_superuser
)
start "kb-admin (API :8002)" cmd /k "%ADMIN_PY% -m uvicorn admin.main:app --host 0.0.0.0 --port 8002 %RELOAD%"

echo ==^> [4/4] Starting admin frontend dev server  (http://localhost:5173) ...
start "kb-admin-ui (Vite :5173)" cmd /k "cd /d %~dp0admin-frontend && npm run dev"

echo.
echo ==^> All started (each service runs in its own window; Ctrl+C stops it):
echo      Core RAG  API : http://localhost:8001   (Swagger: /docs)
echo      Admin     API : http://localhost:8002   (health: /health)
echo      Admin     UI  : http://localhost:5173   (proxies /api, /admin -> :8002)
echo.
echo      To stop: close the windows, or end the python/node processes in Task Manager.
endlocal
