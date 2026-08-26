# KBMS 产品需求文档 (PRD)

> 知识库管理平台 — Knowledge Base Management System
> 版本: v1.0 · 日期: 2026-08-26 · 关联 SPEC: [kbms-spec.md](./kbms-spec.md)

---

## 1. 项目概述

构建一个**集知识维护、多维权限管理、AI 问答鉴权检索、数据看板与知识自动沉淀于一体的知识库管理平台**,在现有 `app/` RAG 引擎之上提供完整的多租户运营能力,支持单篇与批量知识导入、细粒度操作与数据权限控制、智能体鉴权召回、热点 FAQ 挖掘沉淀与知识缺口识别。

---

## 2. 目标用户

| 角色 | 描述 | 主要诉求 |
|---|---|---|
| **系统管理员** | 平台运维负责人 | 用户/部门/角色/权限全量管理,监控运行数据 |
| **知识管理员** | 业务领域的内容负责人 | 知识导入与维护,审核沉淀的 FAQ,管理数据权限 |
| **普通用户 / 提问者** | 一线员工 / 客户 / 内部研究员 | 通过 AI 对话高效检索所需知识,且只能看到被授权的内容 |

---

## 3. 核心功能列表

### 3.1 Must Have (P0 — MVP 阻塞,必须交付)

| # | 功能模块 | 关键能力 |
|---|---|---|
| F-01 | **登录认证** | 账号密码登录、JWT(access+refresh)、Token 刷新、`/me` 获取当前用户身份/部门/角色 |
| F-02 | **用户管理** | 用户列表、新增/编辑、密码重置、启停用、部门归属、角色绑定 |
| F-03 | **部门管理** | 部门树形 CRUD、负责人设置、排序 |
| F-04 | **角色管理与操作权限** | 角色 CRUD、按角色绑定操作权限树(增/删/改/查/AI 访问) |
| F-05 | **知识单元 CRUD** | 知识单元编号、标题、正文、分类、标签、状态、列表分页查询、编辑、查看 |
| F-06 | **知识单文件 / 批量导入** | 支持 PDF、Markdown、Word、TXT,异步解析、向量化、进度可见 |
| F-07 | **数据权限引擎** | 单知识单元配置四类权限实体(`global`/`department`/`role`/`user`)的 OR 混合分配;提供批量校验接口 |
| F-08 | **AI 鉴权问答工作台** | 强制登录态、流式回答、引用来源卡片、未授权召回项的权限缺失提示 |
| F-09 | **数据看板 - 核心指标** | 访问次数、UV、知识单元总数、Token 消耗、平均响应时间 |
| F-10 | **数据看板 - 排行榜** | 高频问题 TOP、最常访问知识单元 TOP |
| F-11 | **FAQ 推荐与审核** | 系统挖掘高频问题生成候选 FAQ,管理员审核通过/驳回,可编辑答案 |
| F-12 | **FAQ 缓存加速** | 审核通过的 FAQ 写入缓存,对话命中时直接返回标准答案 |
| F-13 | **知识缺口识别** | 未命中知识库的提问聚合为缺口清单,展示频次、最近提问时间 |

### 3.2 Should Have (P1 — MVP 后立即补齐)

| # | 功能模块 | 关键能力 |
|---|---|---|
| F-14 | **数据看板 - 趋势图** | 按日/周访问趋势、Token 消耗走势、响应时间分布 |
| F-15 | **登录与个人中心页** | 展示当前用户身份、所属部门、拥有角色(在 AI 工作台侧栏展示) |
| F-16 | **知识单元附件** | 上传附件、下载、删除 |
| F-17 | **知识版本管理** | 同一知识单元的多次编辑产生历史版本,可回滚 |
| F-18 | **问答会话管理** | 历史会话列表、按时间排序、删除会话 |

### 3.3 Nice to Have (P2 — 后续迭代)

| # | 功能模块 | 关键能力 |
|---|---|---|
| F-19 | **SSO / OIDC** | 企业级身份接入(预埋配置位) |
| F-20 | **审计日志** | 全量操作日志查询、导出 |
| F-21 | **Milvus 按组织分片** | 多组织数据物理隔离 |
| F-22 | **多语言 i18n** | 中英双语切换 |
| F-23 | **消息通知** | 知识审核结果通知、FAQ 发布通知 |

---

## 5. 用户故事与验收标准

### F-01 登录认证
**故事**: 作为系统管理员,我希望通过用户名密码登录管理后台,登录后能持续 30 分钟的访问会话。
**验收**:
- [ ] `POST /api/auth/login` 接收 `username`、`password`,正确则返回 `access_token` (30 min) + `refresh_token` (14 d)
- [ ] 错误密码返回 `401` 且不泄露用户是否存在
- [ ] `Authorization: Bearer <token>` 受保护接口未带/过期/伪造 token 时返回 `401`
- [ ] `POST /api/auth/refresh` 用 refresh_token 换新 access_token;refresh_token 失效时返回 `401`
- [ ] `GET /api/auth/me` 返回当前用户 `{id, username, display_name, department_id, roles, permissions}`

### F-02 用户管理
**故事**: 作为系统管理员,我希望创建新员工账号并分配部门和角色。
**验收**:
- [ ] `GET /api/org/users` 支持按部门、角色、状态、用户名分页查询
- [ ] `POST /api/org/users` 创建用户,字段:`username`(唯一)、`display_name`、`password`(明文入库前 bcrypt)、`department_id`、`role_ids`、`status`
- [ ] `PUT /api/org/users/{id}` 编辑用户,密码字段为空则不修改
- [ ] `POST /api/org/users/{id}/reset-password` 重置密码,返回明文密码(一次性)
- [ ] `POST /api/org/users/{id}/toggle-status` 启停用用户
- [ ] 用户名/邮箱唯一冲突时返回 `409`
- [ ] 停用用户登录返回 `401` 友好提示"账号已停用"

### F-03 部门管理
**故事**: 作为系统管理员,我希望建立公司的部门树。
**验收**:
- [ ] `GET /api/org/departments` 返回树形结构(支持扁平或树形两种序列化)
- [ ] `POST /api/org/departments` 创建部门,字段:`name`、`parent_id`(可空,根部门)、`leader_id`(可空)、`sort_order`
- [ ] `PUT /api/org/departments/{id}` 修改部门
- [ ] `DELETE /api/org/departments/{id}` 有子部门或下属用户时拒绝,返回 `409`
- [ ] 部门路径支持后期扩展 LTREE 索引(本期 MVP 用 parent_id 自引用)

### F-04 角色管理与操作权限
**故事**: 作为系统管理员,我希望定义角色并分配操作权限。
**验收**:
- [ ] `GET /api/org/roles` 返回角色列表,字段含 `role_name`、`role_code`、`description`、`permission_count`
- [ ] `POST /api/org/roles` / `PUT /api/org/roles/{id}` / `DELETE /api/org/roles/{id}` CRUD
- [ ] `GET /api/org/permissions` 返回系统全量操作权限树(如 `knowledge:read`、`knowledge:write`、`knowledge:delete`、`ai:access`、`org:read`、`org:write` 等)
- [ ] `POST /api/org/roles/{id}/permissions` 提交 `permission_codes` 列表,全量替换该角色的操作权限
- [ ] 内置 `super_admin`、`knowledge_admin`、`regular_user` 三种角色(seed)

### F-05 知识单元 CRUD
**故事**: 作为知识管理员,我希望对知识单元进行增删改查。
**验收**:
- [ ] `GET /api/knowledge/units` 支持按 `title`、`category`、`status`、`creator_id` 分页
- [ ] `GET /api/knowledge/units/{id}` 返回知识单元详情 + 已配置的数据权限列表
- [ ] `POST /api/knowledge/units` 手动新建(`title`、`content`、`summary`、`category`、`status`)
- [ ] `PUT /api/knowledge/units/{id}` 更新知识单元内容
- [ ] `DELETE /api/knowledge/units` 批量删除(请求体传 `unit_ids` 数组)
- [ ] 字段:`unit_code`(唯一,自动生成 `KU-{yyyymmdd}-{seq}`)、`title`、`content`、`summary`、`category`、`source_file_name`(导入产生)、`file_type`、`file_size`、`status`(`draft`/`published`/`archived`)、`creator_id`

### F-06 知识单文件 / 批量导入
**故事**: 作为知识管理员,我希望上传一份或多份文档自动拆分为知识单元。
**验收**:
- [ ] `POST /api/knowledge/import` 支持单文件与多文件(`files` 数组)
- [ ] 支持格式:PDF、Markdown(.md)、Word(.docx)、TXT
- [ ] 返回 `task_id`,前端按 task_id 轮询解析进度
- [ ] `GET /api/knowledge/tasks/{task_id}` 返回每个文件的解析状态与产生的 `unit_id`
- [ ] 解析失败的单个文件不影响其他文件继续
- [ ] 导入完成后自动向量化(Milvus),通过 RAG 服务完成检索

### F-07 数据权限引擎
**故事**: 作为知识管理员,我希望对每个知识单元精确控制谁能访问。
**验收**:
- [ ] `GET /api/knowledge/units/{id}/permissions` 列出该单元已配置的数据权限
- [ ] `POST /api/knowledge/units/{id}/permissions` 提交 `permissions` 数组,每个元素含 `target_type` ∈ {`global`, `department`, `role`, `user`} 和 `target_id`(`global` 时为 `null`)
- [ ] 支持同一知识单元混合配置多类多实体
- [ ] `POST /api/knowledge/check-permissions` 提交 `{user_id, unit_ids[]}`,响应 `{authorized_unit_ids[], unauthorized_unit_ids[]}`
- [ ] 校验规则:`global` → 全员通过;`department` → 用户部门命中即通过;`role` → 用户任一角色命中即通过;`user` → 用户本人命中即通过(OR 逻辑)
- [ ] 知识单元默认无任何权限配置时,所有用户均无权访问(返回 `403` + 知识缺失提示)

### F-08 AI 鉴权问答工作台
**故事**: 作为普通用户,我希望登录后提问并获得带引用来源的回答,且不会看到我无权访问的内容。
**验收**:
- [ ] 工作台入口强制登录(未登录跳转到 `/login`)
- [ ] `POST /api/ai/chat/stream` SSE 流式响应,请求体 `{question, session_id?}`
- [ ] 响应事件类型:`recall`(召回的候选)、`authorized`(通过的引用)、`unauthorized`(无权限的提示)、`token`(流式 token)、`done`(结束)、`error`
- [ ] 召回到无权限知识单元时,在引用区追加"⛔ 知识单元 #xxx 您当前无权访问,如有需要请联系管理员"
- [ ] 调用顺序:用户登录态校验 → RAG 召回候选 → 调用 `check-permissions` 过滤 → 组装 Context → LLM 流式生成
- [ ] 异步落 `qa_access_logs`(包含 user_id、session_id、question、answer、recalled/authorized/unauthorized unit_ids、token 计数、响应耗时)
- [ ] FAQ 缓存优先:若命中已发布 FAQ,跳过 RAG 调用,直接输出标准答案 + 来源标识 `source:faq`

### F-09 数据看板 - 核心指标
**故事**: 作为系统管理员,我希望首页看到平台的整体运行数据。
**验收**:
- [ ] `GET /api/dashboard/metrics` 响应:
  ```json
  {
    "total_visits": 1234,
    "unique_visitors": 56,
    "total_knowledge_units": 789,
    "total_tokens": 2345678,
    "avg_response_time_ms": 1820
  }
  ```
- [ ] 支持 `range` 参数:`today` / `7d` / `30d` / `all`(默认 7d)

### F-10 数据看板 - 排行榜
**故事**: 作为系统管理员,我希望看到最常被问到的问题和最常被引用的知识单元。
**验收**:
- [ ] `GET /api/dashboard/rankings/questions?limit=10` 返回 TOP 高频问题(按出现次数降序,需语义去重聚类)
- [ ] `GET /api/dashboard/rankings/units?limit=10` 返回最常被引用的知识单元 TOP 榜

### F-11 FAQ 推荐与审核
**故事**: 作为知识管理员,我希望系统自动挖掘高频问题,我审核后发布。
**验收**:
- [ ] 后台定时任务(`FAQ_MINER_INTERVAL_MIN`,默认 60 分钟)或每次会话结束触发聚类:
  - 对历史 `qa_access_logs.question` 做语义去重(embedding + 阈值)
  - 频次 ≥ `FAQ_MIN_FREQ_THRESHOLD`(默认 5)且当前未发布的问题 → 生成候选 FAQ
  - 关联最常被引用的 `related_unit_id`,自动生成 `answer`(取最近一次被采纳的回答或 LLM 改写)
- [ ] `GET /api/settlement/faqs/recommendations` 返回 `status=pending_review` 的候选
- [ ] `POST /api/settlement/faqs/{id}/review` 请求体 `{action: approve|reject, edited_answer?}`
- [ ] 通过 → `status=published` 且写入 FAQ 缓存(Redis 或进程内 LRU,本期 MVP 用进程内 LRU + 持久化到 Postgres)
- [ ] 驳回 → `status=rejected`

### F-12 FAQ 缓存加速
**故事**: 作为普通用户,当我提问命中已发布 FAQ 时,应能立即得到标准答案。
**验收**:
- [ ] 缓存匹配策略:精确字符串 + 语义相似度(embedding 余弦 ≥ `FAQ_MATCH_THRESHOLD`,默认 0.85)
- [ ] 命中时 SSE 直接推送 `answer` 全文 + `source:faq` + `faq_id`
- [ ] 缓存命中仍写入 `qa_access_logs`(便于统计)
- [ ] 已发布 FAQ 被删除或下线时,同步失效缓存项

### F-13 知识缺口识别
**故事**: 作为知识管理员,我希望看到 AI 没有回答好的问题,以便补全知识。
**验收**:
- [ ] 缺口判定:RAG 召回 top-k 相似度均 < `GAP_SIM_THRESHOLD`(默认 0.6),或 FAQ 缓存/知识库均无匹配
- [ ] 聚合:同一 `question_pattern`(标准化后)累计 `ask_count`,记录 `last_asked_at`
- [ ] `GET /api/settlement/knowledge-gaps` 分页返回 `status=unresolved` 缺口
- [ ] 支持状态流转:`unresolved` → `resolved`(已创建关联知识单元) / `ignored`(管理员标记)
- [ ] 一键创建关联知识单元:基于缺口样本生成草稿,管理员补充后发布

### F-14 数据看板 - 趋势图
**故事**: 作为系统管理员,我希望看访问量、Token、响应时间的趋势变化。
**验收**:
- [ ] `GET /api/dashboard/stats/tokens?range=7d` 返回按日聚合的 `{date, prompt_tokens, completion_tokens, total_tokens, avg_response_time_ms, visit_count}`
- [ ] 前端用 ECharts / Ant Design Charts 渲染折线图

### F-18 问答会话管理
**故事**: 作为普通用户,我希望保留历史对话并能切换查看。
**验收**:
- [ ] `GET /api/ai/sessions` 返回当前用户的会话列表(按更新时间倒序)
- [ ] `GET /api/ai/sessions/{id}/messages` 返回会话内的问答历史
- [ ] `DELETE /api/ai/sessions/{id}` 删除会话

---

## 6. 非功能需求

### 6.1 性能
| 指标 | 目标 |
|---|---|
| 登录接口 P95 响应 | < 300 ms |
| AI 问答首 token 延迟 (P95) | < 2 s |
| 数据看板指标查询 P95 | < 1 s |
| 知识列表分页查询 P95 (100 万行) | < 500 ms (Postgres 索引覆盖) |
| 单文件解析 (10MB) | < 30 s |
| 批量导入 (50 文件) | 不阻塞 UI,BackgroundTasks 异步执行 |
| FAQ 命中响应 (P95) | < 100 ms |

### 6.2 安全
- **传输**: 强制 HTTPS(生产),开发可用 HTTP。
- **密码**: bcrypt(cost ≥ 12),数据库只存哈希,不存明文。
- **JWT**: HS256,secret 长度 ≥ 32 字节,启动校验;access TTL 30 min,refresh TTL 14 d;支持主动失效(可选 Redis 黑名单,本期不强制)。
- **RBAC**: 操作权限按角色分配,中间件统一拦截,无权限接口返回 `403`。
- **数据权限**: AI 检索召回后必须经 `check-permissions` 鉴权,不可绕过。
- **审计**: 所有写操作记 `audit_logs`(本期仅落 logger 文件,后续进库)。
- **注入防护**: Pydantic v2 严格模式校验所有入参,SQLAlchemy 参数化查询,无字符串拼接。
- **CORS**: 由 `*` 收敛为具体域名列表(开发可用 `localhost` 白名单)。
- **文件上传**: 文件类型白名单(MIME + 扩展名双校验),单文件 ≤ 50 MB。

### 6.3 兼容性
- **浏览器**: Chrome / Edge 最新两个大版本 + Safari 16+;移动端不做专门适配但保证布局可读。
- **后端**: Python 3.11+,与现有 `app/` 共享 3.11+ 镜像。
- **存储**: Postgres 16 / SQLAlchemy 2.x async / Alembic。
- **RAG 集成**: 通过 HTTP 调用现有 RAG 服务(`RAG_BASE_URL`),不修改 RAG 核心代码,仅在请求头透传 `X-User-Id`、`X-Session-Id`(可选)。
- **前端**: Node 20+ / Vite 5+ / React 18 / TypeScript 5 / Ant Design 5 / ECharts 5。

### 6.4 可观测性
- **日志**: colorlog + TimedRotatingFileHandler,统一格式 `%(asctime)s [%(levelname)s] %(name)s: %(message)s`,日志文件按天滚动、保留 30 天。
- **请求追踪**: 中间件记录每个请求的方法、路径、状态码、耗时。
- **关键事件**: 登录、权限变更、知识导入完成、FAQ 发布写入 ERROR/INFO 级日志。

### 6.5 可维护性
- **代码分层**: `api / core / db / domain / schemas / services / utils` 严格分层,核心业务逻辑放 `services/`,不放进 router。
- **配置**: `.env` + `pydantic-settings`,新增配置项必须带类型与默认值(可选)或强制必填。
- **迁移**: Alembic 命名规范 `0001_init.py`、`0002_xxx.py`,每次迁移必须有对应的 downgrade。
- **依赖**: `pyproject.toml` 锁定版本范围,`uv lock` 提交。
- **种子数据**: 首次部署后通过 `scripts/create_superuser.py` + Alembic data migration 自动初始化权限码和内置角色。

### 6.6 可用性
- **健康检查**: `GET /health` 返回 `{status, db, redis?, rag_reachable}`。
- **优雅降级**: RAG 服务不可达时,AI 问答返回 `503` + 友好提示,不直接报错堆栈。
- **离线缓存**: FAQ 缓存保证 RAG 短暂不可用时仍能提供问答。

---

## 7. 交付物清单

| 交付物 | 路径 |
|---|---|
| KBMS 后端服务 | `admin/` |
| KBMS 前端 SPA | `admin-frontend/` |
| 数据库迁移脚本 | `admin/db/migrations/versions/` |
| 初始化脚本(超级用户) | `admin/scripts/create_superuser.py` |
| API 文档(自动生成) | `http://<host>:8002/docs` (FastAPI Swagger) |
| 示例知识文档数据 | `admin/scripts/sample_knowledge/`(3-5 篇 PDF/MD) |
| 完整业务演示链路 | `docs/kbms-demo.md` |
| Docker 编排 | `docker-compose.yml`(扩展 `postgres` 和 `kb-admin`) |
| 本 PRD | `plan/kbms-prd.md` |
| 技术规范 SPEC | `plan/kbms-spec.md` |

---

## 8. 验收标准(总体)

1. ✅ 能完成用户登录、角色管理、部门管理与菜单/按钮级操作权限分配
2. ✅ 能通过界面完成单篇与批量文档导入,并成功将文档拆分为知识单元完成检索入库
3. ✅ 能对知识单元执行增删改查,并支持混合配置全局、部门、角色、个人四类数据权限
4. ✅ 能在用户满足部门、角色、个人或全局中任意一种权限时正常访问知识单元
5. ✅ 能在 AI 对话中强制校验登录态并调用鉴权接口过滤未授权知识单元,对无权限召回项输出明确权限缺失提示
6. ✅ 能在数据看板正确展示访问次数、独立人数、知识单元数、常见问题榜、知识热度榜、Token 消耗与响应时间趋势
7. ✅ 能自动从历史对话中挖掘高频问题并生成推荐 FAQ,支持管理员审核发布并写入缓存加速应答
8. ✅ 能自动识别未命中知识库的问题并生成知识缺口列表,支持查看提问频次
9. ✅ `docker compose up` 一键拉起 RAG + KBMS + Postgres,5 分钟内可演示完整业务链路
10. ✅ `GET /api/dashboard/metrics` 在 7d 数据 100 万条下 P95 < 1 s