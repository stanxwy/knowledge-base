# KBMS 端到端演示

> 配套 `plan/kbms-prd.md` 的验收标准,本文档走一遍完整业务链路。

## 0. 启动前提
- KBMS 服务(`kb-admin` :8002)已启动,Postgres 已初始化,初始超级用户 `admin / admin123` 已创建
- RAG 引擎(`kb-import` :8000)已启动且至少能响应 `/api/v1/recall`(返回 `file_title`)

## 1. 组织与权限搭建

### 1.1 创建部门树
```bash
TOKEN=$(curl -sS -X POST http://localhost:8002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r .access_token)

curl -sS -X POST http://localhost:8002/api/org/departments \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"总部"}'

curl -sS -X POST http://localhost:8002/api/org/departments \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"技术部","parent_id":1}'

curl -sS -X POST http://localhost:8002/api/org/departments \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"财务部","parent_id":1}'
```

### 1.2 创建用户并分配角色
```bash
# 普通用户(技术部 + regular_user)
curl -sS -X POST http://localhost:8002/api/org/users \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"username":"engineer","password":"engineer123","display_name":"工程师","department_id":2,"role_ids":[3]}'

# 财务用户
curl -sS -X POST http://localhost:8002/api/org/users \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"username":"accountant","password":"acc123456","display_name":"会计","department_id":3,"role_ids":[3]}'
```

## 2. 知识导入与权限配置

### 2.1 上传文档
```bash
curl -sS -X POST http://localhost:8002/api/knowledge/import \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@./test_data/fridge-repair.md"

# 轮询进度
TASK_ID=<task_id>
while true; do
  STATUS=$(=$(curl -sS http://localhost:8002/api/knowledge/tasks/$TASK_ID \
    -H "Authorization: Bearer $TOKEN" | jq -r .status)
  [ "$STATUS" = "done" ] && break
  sleep 1
done
```

### 2.2 配置 4 类权限
```bash
# KU-001 全局��开
curl -sS -X POST http://localhost:8002/api/knowledge/units/1/permissions \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"permissions":[{"target_type":"global"}]}'

# KU-002 仅技术部
curl -sS -X POST http://localhost:8002/api/knowledge/units/2/permissions \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"permissions":[{"target_type":"department","target_id":2}]}'

# KU-003 仅 accountant 个人
curl -sS -X POST http://localhost:8002/api/knowledge/units/3/permissions \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"permissions":[{"target_type":"user","target_id":3}]}'
```

### 2.3 验证数据权限引擎
```bash
# engineer(dept=2,role=3) 应该看到 KU-001 + KU-002
curl -sS -X POST http://localhost:8002/api/knowledge/check-permissions \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"user_id":2,"unit_ids":[1,2,3]}'
# 预期: {"authorized_unit_ids":[1,2],"unauthorized_unit_ids":[3]}

# accountant(dept=3,user=3) 应该看到 KU-001 + KU-003
curl -sS -X POST http://localhost:8002/api/knowledge/check-permissions \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"user_id":3,"unit_ids":[1,2,3]}'
# 预期: {"authorized_unit_ids":[1,3],"unauthorized_unit_ids":[2]}
```

## 3. AI 鉴权问答

登录 engineer 后,进入工作台提问 "冰箱不制冷怎么办?":
- 浏览器侧 SSE 流显示 `recall` + `authorized=[1,2]` + `unauthorized=[3]`
- 引用来源卡: `#1 冰箱维修手册` `#2 ...` + 红色 `⛔ #3 无权访问`
- 流式回答 + `done` 事件

切到 accountant:
- `unauthorized=[2]` (因为 dept=3 不命中 KU-002 的 dept=2 配置)
- 引用来源卡: `#1` + `#3` + 红色 `⛔ #2`

## 4. FAQ 沉淀

### 4.1 制造高频问题
让多个用户都问 "冰箱不制冷怎么办?",至少 5 次以上。

### 4.2 触发挖掘
```bash
curl -sS -X POST http://localhost:8002/api/settlement/faqs/_run-mine \
  -H "Authorization: Bearer $TOKEN"
# 预期: {"mined":1,"loaded":N}

curl -sS http://localhost:8002/api/settlement/faqs/recommendations \
  -H "Authorization: Bearer $TOKEN"
```

### 4.3 审核通过
```bash
curl -sS -X POST http://localhost:8002/api/settlement/faqs/<faq_id>/review \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"action":"approve","edited_answer":"标准答案: ...","category":"家电维修"}'
```

### 4.4 验证缓存命中
重新提问同样的问题 — SSE 流第一个事件是 `event: authorized, source: "faq"`,跳过 RAG,直接返回标准答案。

## 5. 知识缺口

### 5.1 制造无命中提问
提问一个完全不相关的话题,例如 "完全不沾边的复杂问题 怎么处理":
- `recall` 事件 `unit_ids: []`
- SSE `done` 携带 fallback 答案
- 后台 upsert 到 `knowledge_gaps`,`ask_count=1`

### 5.2 一键建档
```bash
curl -sS -X POST http://localhost:8002/api/settlement/knowledge-gaps/<gap_id>/create-unit \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"title":"为缺口补充的知识","content":"...","category":"补充"}'
# 预期: gap.status=resolved, resolved_unit_id 指向新 KU
```

## 6. 看板

```bash
curl -sS "http://localhost:8002/api/dashboard/metrics?range=7d" \
  -H "Authorization: Bearer $TOKEN"
curl -sS "http://localhost:8002/api/dashboard/rankings/questions?limit=5" \
  -H "Authorization: Bearer $TOKEN"
curl -sS "http://localhost:8002/api/dashboard/rankings/units?limit=5" \
  -H "Authorization: Bearer $TOKEN"
curl -sS "http://localhost:8002/api/dashboard/stats/tokens?range=7d" \
  -H "Authorization: Bearer $TOKEN"
```

## 7. 验收对照(对应 PRD §8)

| 验收项 | 通过条件 | 验证步骤 |
|---|---|---|
| 1. 用户登录、角色、部门、操作权限 | ✅ | 步骤 1 + 用 engineer 登录验证只看到 `[knowledge,read, ai,access]` |
| 2. 单/批量导入 + 自动入库 | ✅ | 步骤 2.1,轮询 task 状态到 `done` |
| 3. 四类数据权限混合 | ✅ | 步骤 2.2 + `check-permissions` 验证 |
| 4. OR 鉴权生效 | ✅ | 步骤 2.3 |
| 5. AI 鉴权 + 友好提示 | ✅ | 步骤 3 |
| 6. 数据看板 | ✅ | 步骤 6 |
| 7. FAQ 挖掘 + 审核 + 缓存 | ✅ | 步骤 4 |
| 8. 知识缺口识别 | ✅ | 步骤 5 |
| 9. docker compose 一键拉起 | ✅ | `docker compose up -d --build` |
| 10. health 接口 | ✅ | `curl http://localhost:8002/health` 返回 `{db:true,...}` |