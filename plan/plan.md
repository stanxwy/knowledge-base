# KBMS 实施计划 (Implementation Plan)

> 与 [kbms-prd.md](../plan/kbms-prd.md) + [kbms-spec.md](../plan/kbms-spec.md) 对齐。
> 日期: 2026-08-26 · 范围: 完整 PRD(Must Have + Should Have)。

---

## Context

`d:/code/atguigu/knowledge-base/app/` 是一个**单租户纯 RAG 引擎**(FastAPI + LangGraph + Milvus + Mongo + MinIO + DashScope/BGE-M3),用于文档型 RAG 问答,**没有任何用户/组织/权限脚手架**。

现在要在 RAG 之上构建一套**生产可用的 KBMS**:登录认证、组织/角色/部门/操作权限、知识单元 CRUD 与数据权限配置(全局/角色/部门/个人 OR 混合)、AI 鉴权问答流、数据看板、FAQ 自动挖掘与审核发布、知识缺口识别。交付物见 PRD §7。

**已确认决策**:
1. **同仓库独立子应用**:新增 `admin/`(FastAPI 独立进程,端口 8002)与 `admin-frontend/`(React SPA)。
2. **Postgres + SQLAlchemy async + Alembic** 作为 KBMS 主库。
3. **admin 通过 HTTP 调用 RAG**(不修改 RAG 工作流核心,只在 RAG 端新增两个最小辅助接口:`/api/v1/recall`、`/api/v1/embed`,~50 行代码)。
4. **JWT (HS256)** + bcrypt,access TTL 30 min / refresh TTL 14 d。
5. **FAQ 缓存**: 进程内 LRU(`cachetools`)+ 持久化到 Postgres,后期可换 Redis。
6. **APScheduler** 跑 FAQ 挖掘与缺口聚合定时任务。

---

## 目标架构

```
/ (仓库根)
├── app/                       # 现有 RAG 引擎 — 仅新增 2 个最小辅助路由
├── admin/                     # ★ NEW — KBMS 后端 (FastAPI 独立进程, :8002)
├── admin-frontend/            # ★ NEW — React + AntD SPA
├── docker-compose.yml         # 扩展 — postgres / kb-admin
└── plan/
    ├── kbms-prd.md            # ★ NEW
    ├── kbms-spec.md           # ★ NEW
    └── kbms-impl-plan.md      # ★ 本文件
```

### 端口
| 服务 | 端口 | 说明 |
|---|---|---|
| `kb-import` | 8000 | RAG 摄入(不变) |
| `kb-query` | 8001 | RAG 问答(不变) |
| **`kb-admin`** | **8002** | KBMS 后端 + 托管 admin SPA |
| `postgres` | 5432 | KBMS 主库 |
| Milvus / Mongo / MinIO | 不变 | **Neo4j 从 compose 移除**(代码未引用) |

---

## 关键集成点(RAG ↔ KBMS)

### RAG 端新增(2 个路由,~50 行)
| 接口 | 用途 | admin 调用方式 |
|---|---|---|
| `POST /api/v1/recall` | 入参 `{query, top_k}` → 出参 `{unit_ids[], scores[]}` | admin 在 AI 鉴权问答流中先召回,再调 `check-permissions` |
| `POST /api/v1/embed` | 入参 `{texts[]}` → 出参 `{vectors[][]}` (BGE-M3) | admin 用作 FAQ 语义匹配与缺口聚类 |

> 实现位置:`app/api/v1/recall_router.py`、`app/api/v1/embed_router.py`,复用现有 `get_embedder` 与 Milvus 服务工厂,只暴露少量必要字段。

### admin 端调用 RAG
- `RAG_BASE_URL` 配置为 `http://kb-import:8000`(容器内)或 `http://localhost:8000`(本地)。
- 使用 `httpx.AsyncClient` 调用,带 `X-User-Id`、`X-Session-Id` 头(供 RAG 端可选记录)。
- 所有调用集中在 `admin/services/rag_client.py`。

### 数据归属
- 知识向量仍存在 RAG 的 Milvus 全局集合中;admin 端 `knowledge_units` 存元数据 + 数据权限,通过 `unit_code`/`file_title` 与 RAG 端对齐。
- MVP **不做** Milvus 按组织分片(SPEC §2.4 文档化)。

---

## 关键文件清单

### A.1 新增(后端 `admin/`)

**核心脚手架**
- `admin/pyproject.toml`、`admin/.env.example`、`admin/alembic.ini`
- `admin/main.py`(FastAPI 入口 + lifespan + 静态文件 + CORS)
- `admin/core/config.py`、`admin/core/security.py`(bcrypt + JWT)、`admin/core/exceptions.py`、`admin/core/logging.py`
- `admin/db/base.py`(async engine + DeclarativeBase + sessionmaker + get_db dep)
- `admin/db/migrations/env.py`、`admin/db/migrations/versions/0001_init.py`、`admin/db/migrations/versions/0002_seed.py`
- `admin/scripts/create_superuser.py`

**领域模型** (`admin/domain/`)
- `user.py`、`department.py`、`role.py`、`permission.py`、`knowledge_unit.py`、`unit_permission.py`、`ai_session.py`、`ai_message.py`、`qa_access_log.py`、`faq.py`、`knowledge_gap.py`、`audit_log.py`

**Pydantic schemas** (`admin/schemas/`)
- `auth.py`、`org.py`、`knowledge.py`、`ai.py`、`dashboard.py`、`settlement.py`、`common.py`

**业务层** (`admin/services/`)
- `auth_service.py`、`user_service.py`、`department_service.py`、`role_service.py`
- `knowledge_service.py`、`data_permission_engine.py` ★、`importer.py`
- `ai_service.py` ★(流式编排)、`rag_client.py` ★(httpx)、`faq_cache.py` ★、`faq_miner.py` ★、`gap_detector.py` ★、`dashboard_service.py`、`audit_service.py`

**API 路由** (`admin/api/`)
- `deps.py`: `get_db`、`get_current_user`、`require_permission`、`require_superuser`
- `v1/auth.py`、`v1/org/{users,departments,roles,permissions}.py`
- `v1/knowledge/{units,permissions,import_tasks,importer}.py`
- `v1/ai/{chat,sessions}.py`
- `v1/dashboard/stats.py`
- `v1/settlement/{faqs,gaps}.py`

**部署**
- `admin/Dockerfile`
- `admin/static/dist/`(由 `admin-frontend-build` 服务注入)

### A.2 新增(前端 `admin-frontend/`)

- `package.json`、`vite.config.ts`、`tsconfig.json`、`index.html`
- `src/main.tsx`、`src/App.tsx`、`src/router.tsx`(含路由守卫)
- `src/store/auth.ts`(zustand)
- `src/api/`:`client.ts`(axios + JWT interceptor + 401 refresh)、`auth.ts`、`org.ts`、`knowledge.ts`、`ai.ts`(EventSource SSE)、`dashboard.ts`、`settlement.ts`
- `src/components/`:`Layout.tsx`(动态菜单)、`PermissionSelector.tsx`、`KnowledgeImporter.tsx`、`StreamMarkdown.tsx`、`UnauthorizedBanner.tsx`、`Charts.tsx`
- `src/pages/`:
  - `Login.tsx`
  - `Dashboard.tsx`(指标卡 + 排行 + 趋势)
  - `org/{Users,Departments,Roles,Permissions}.tsx`
  - `knowledge/{List,Edit,Import}.tsx`
  - `ai/Workbench.tsx`
  - `settlement/{FaqReview,Faqs,Gaps}.tsx`
- `src/locales/zh.ts`

### A.3 修改(最小侵入)

**RAG 端(只新增辅助路由)**
- `app/api/v1/recall_router.py` ★ NEW — `POST /api/v1/recall`
- `app/api/v1/embed_router.py` ★ NEW — `POST /api/v1/embed`
- `app/main.py` — include 新路由(其余不变)
- `app/api/middleware/cors.py` — 把 `allow_origins=["*"]` 收敛为配置项 `BACKEND_CORS_ORIGINS` 驱动

**运维**
- `docker-compose.yml` — 加 `postgres`、`kb-admin` 服务;**移除 `app/docker-compose.yml` 中的 Neo4j 服务**
- `.env.example` — 加 `KBMS_*` 段:`POSTGRES_*`、`JWT_SECRET`、`JWT_*_TTL`、`INITIAL_SUPERUSER_*`、`RAG_BASE_URL`、`FAQ_MIN_FREQ_THRESHOLD`、`FAQ_MATCH_THRESHOLD`、`GAP_SIM_THRESHOLD`
- `README.cn.md` — 新增"KBMS"章节,模块图 + 端口表 + 启动命令

### A.4 不动
- RAG 工作流所有 LangGraph 节点、`factories/`、`domain/ports/`、`workflows/`、嵌入/检索/重排实现 — 一行不改。
- `app/static/pages/{chat,ingest}.html` — 不动,匿名 RAG 端用户继续使用。

---

## 实施顺序(增量、可独立提交)

### 阶段 0:文档(已完成)
- [x] PRD `plan/kbms-prd.md`
- [x] SPEC `plan/kbms-spec.md`
- [x] 实施计划 `plan/kbms-impl-plan.md`(本文件)

### 阶段 1:admin/ 后端基础 + 认证(独立可演示)
1. `admin/pyproject.toml` + `.env.example` + `admin/main.py`(空 FastAPI)
2. `admin/core/{config,security,exceptions,logging}.py`
3. `admin/db/base.py`(async engine)
4. `admin/db/migrations/env.py` + `alembic.ini` + `0001_init.py`(建 users/departments/roles/permissions/user_roles/role_permissions)
5. `0002_seed.py`(种子权限码 + 内置三角色)
6. `admin/domain/{user,department,role,permission}.py`
7. `admin/schemas/auth.py` + `admin/services/auth_service.py` + `admin/api/deps.py`
9. `admin/api/v1/auth.py`(login/refresh/logout/me)
10. `admin/scripts/create_superuser.py`
11. **里程碑 1 验证**: `alembic upgrade head` + 启动 admin + `curl /api/auth/login admin/admin123` 拿 token + `curl /api/auth/me`。

### 阶段 2:组织/用户/部门/角色完整 CRUD
1. `admin/schemas/org.py`
2. `admin/services/{user,department,role}_service.py`
3. `admin/api/v1/org/{users,departments,roles,permissions}.py`
4. **里程碑 2 验证**: 通过 Swagger `/docs` 创建部门→角色→用户→分配角色→登录新用户看到正确权限。

### 阶段 3:知识维护 + 数据权限引擎
1. `admin/domain/{knowledge_unit,unit_permission}.py` + 0003 迁移
2. `admin/schemas/knowledge.py`
3. `admin/services/{knowledge_service,data_permission_engine}.py`
4. `admin/api/v1/knowledge/{units,permissions}.py`
5. **里程碑 3 验证**: 创建知识单元 → 配置 4 类数据权限 → `check-permissions` 接口正确分流。

### 阶段 4:RAG 集成 + 文档导入
1. `admin/services/rag_client.py`(httpx 封装 recall/embed/upload)
2. `app/api/v1/recall_router.py` + `app/api/v1/embed_router.py` + `app/main.py` include
3. `app/api/middleware/cors.py` 收敛配置
4. `admin/services/importer.py`(pypdf/python-docx/markdown 解析)
5. `admin/api/v1/knowledge/importer.py` + `admin/api/v1/knowledge/import_tasks.py` + 后台任务表
6. **里程碑 4 验证**: 上传 PDF → 看到 task 进度 → 知识单元列表出现新条目 → 通过 recall 接口验证 Milvus 中存在。

### 阶段 5:AI 鉴权问答流(SSE)
1. `admin/domain/{ai_session,ai_message,qa_access_log}.py` + 0004 迁移
2. `admin/schemas/ai.py`
3. `admin/services/ai_service.py`(SSE 编排:FAQ 缓存优先 → recall → check-permissions → 流式生成 → 落日志 → 缺口检测)
4. `admin/services/faq_cache.py`(内存 LRU + 持久化)
5. `admin/api/v1/ai/{chat,sessions}.py`
6. **里程碑 5 验证**: 用 admin SPA 提问 → 看到流式回答 + 引用来源卡 + 无权限提示 + qa_access_logs 入库。

### 阶段 6:数据看板
1. `admin/domain/sqa_access_log.py` 完善(已有,补索引)
2. `admin/services/dashboard_service.py`(聚合查询,SQL 写到位)
3. `admin/schemas/dashboard.py`
4. `admin/api/v1/dashboard/stats.py`
5. **里程碑 6 验证**: `curl /api/dashboard/metrics?range=7d` 返回 5 个核心指标 + `rankings/{questions,units}` + `stats/tokens`。

### 阶段 7:知识沉淀 + 缺口识别
1. `admin/domain/{faq,knowledge_gap}.py` + 0005 迁移
2. `admin/services/{faq_miner,gap_detector}.py` + APScheduler lifespan
3. `admin/schemas/settlement.py`
4. `admin/api/v1/settlement/{faqs,gaps}.py`
5. **里程碑 7 验证**: 制造 5+ 条相同提问日志 → 触发挖掘 → 看到 FAQ 推荐 → 审核通过 → 缓存命中 → 制造低相似度问题 → 缺口列表出现。

### 阶段 8:admin-frontend SPA
按 SPEC §4 的页面拆,本阶段交付一个**全部 13 个页面**可用的 SPA。
1. 脚手架 + 路由 + 登录 + Layout
2. 组织/用户/部门/角色页
3. 知识列表/详情/编辑/导入页(重点 PermissionSelector + Importer)
4. AI 工作台(流式 + 引用卡)
6. 数据看板(指标 + 排行 + 趋势)
7. FAQ 审核 + 已发布 + 缺口
8. **里程碑 8 验证**: 全链路 UI 演示。

### 阶段 9:docker-compose + 文档收尾
1. `docker-compose.yml` 加 `postgres`、`kb-admin`、`admin-frontend-build`(`profiles:[build]`)
2. 移除 `app/docker-compose.yml` 中的 Neo4j
3. `.env.example` 完善 + `app/.env.prod` 加 KBMS 段
4. `README.cn.md` 加 KBMS 章节
5. `docs/kbms-demo.md` 写演示脚本
6. **里程碑 9 验证**: `docker compose up -d` 一键拉起 RAG + KBMS + Postgres + 前端构建产物。

---

## 端到端验证(对应 PRD §8 验收标准)

1. **认证与权限**
   - `POST /api/auth/login admin/admin123` → 200 + tokens
   - `POST /api/auth/login admin/wrong` → 401
   - 普通用户调 `POST /api/org/users` → 403(无 `user:write`)
   - 跨部门用户读他人知识 → 403 + banner
2. **知识导入**
   - 上传 3 文件(分别 PDF/MD/DOCX) → 进度可见
   - 完成后知识单元列表出现 3 条 `status=draft`
   - 自动向量化完成,Milvus 中可被 recall
3. **数据权限**
   - 给 KU-001 配置 global + role:知识管理员
   - 普通用户被授 role:知识管理员 → 可访问
   - 撤销角色后 → 访问 403
4. **AI 鉴权问答**
   - 提问命中已发布 FAQ → 立刻返回(source:faq),qa_access_logs 入库
   - 提问命中普通知识 → 流式返回 + 引用来源卡
   - 提问召回到无权限知识 → 流式 + 无权限提示卡
5. **看板**
   - `GET /api/dashboard/metrics?range=7d` → 5 字段
   - `rankings/questions` 与 `rankings/units` 非空
6. **FAQ 沉淀**
   - 同一问题被问 5 次 → 候选 FAQ 出现
   - 审核通过 → 已发布 + 缓存命中
7. **缺口识别**
   - 制造 3 个完全不同领域提问 → 缺口列表出现
8. **生产镜像**
   - `docker compose up -d` → 5 个服务健康
   - `curl http://localhost:8002/health` → `{status: ok}`

---

## 风险与缓解

| 风险 | 缓解 |
|---|---|
| 修改 RAG 影响现有 query 行为 | **不修改**。新增 `/api/v1/recall` 与 `/api/v1/embed` 是独立路由,挂在 `app/main.py` 的 `include_router`,不触碰现有 router |
| admin 需读取 embedding 导致模型双部署 | 通过 RAG 新�� `/api/v1/embed` 接口代理 BGE-M3,admin 不直接加载模型 |
| CORS 改动可能影响 chat.html | `BACKEND_CORS_ORIGINS` 保留 `["*"]` 作为默认值,生产部署时按需收敛 |
| Postgres 单点 | docker compose 部署 + `volumes/postgres`,生产建议托管 RDS |
| JWT secret 泄露 | 启动校验 `JWT_SECRET` 长度 ≥ 32,`.env.prod` 不入 git |
| FAQ 嵌入语义匹配召回质量 | `FAQ_MATCH_THRESHOLD` 默认 0.85,可在线调整;后期可换 Milvus 单独索引 |
| 文档解析大 PDF 超时 | 切片策略:每块 1500 字;解析放后台,前端轮询;失败单文件不影响整体 |
| APScheduler 单进程 | MVP 接受单进程;多 worker 时换 Redis 锁,文档化 |

---

## 后续工作(P2,本期不做)
- SSO/OIDC(MVP 之后,预埋 `OIDC_*` env 位)
- 审计日志进库(本期落 logger 文件)
- Milvus 按组织分片
- 多语言 i18n
- 消息通知
- 知识版本管理 + 附件