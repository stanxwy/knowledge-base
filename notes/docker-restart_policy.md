## `restart: unless-stopped` vs `restart: always` 的区别

这两种策略的主要区别在于**容器被手动停止后的行为**。

### 核心区别

| 特性 | `unless-stopped` | `always` |
|------|------------------|----------|
| **Docker 重启后** | ✅ 自动启动 | ✅ 自动启动 |
| **虚拟机重启后** | ✅ 自动启动 | ✅ 自动启动 |
| **容器崩溃后** | ✅ 自动重启 | ✅ 自动重启 |
| **手动停止后** | ❌ **不会再自动启动** | ✅ **Docker 重启后仍会启动** |

### 详细对比

#### 1. `unless-stopped`（推荐）

```yaml
restart: unless-stopped
```

**行为：**
- 容器异常退出 → ✅ 自动重启
- Docker 服务重启 → ✅ 自动启动
- 虚拟机重启 → ✅ 自动启动
- **用户手动停止（`docker stop`）→ ❌ 不会自动启动**

**优点：**
- 给管理员**完全控制权**
- 手动停止后不会意外重启
- 适合生产环境

**示例场景：**
```bash
# 手动停止容器
docker stop milvus-attu

# 重启 Docker 服务
systemctl restart docker

# 容器不会自动启动（因为手动停止过）
docker ps | grep milvus-attu  # 没有输出
```

#### 2. `always`

```yaml
restart: always
```

**行为：**
- 容器异常退出 → ✅ 自动重启
- Docker 服务重启 → ✅ 自动启动
- 虚拟机重启 → ✅ 自动启动
- **用户手动停止（`docker stop`）→ ✅ Docker 重启后仍会启动**

**缺点：**
- 即使手动停止，Docker 重启后仍会启动
- **可能导致意外启动**
- 需要额外的命令才能永久停止

**示例场景：**
```bash
# 手动停止容器
docker stop milvus-attu

# 重启 Docker 服务
systemctl restart docker

# 容器会自动启动（即使之前手动停止过）
docker ps | grep milvus-attu  # 显示容器正在运行
```

### 如何永久停止 `always` 策略的容器

如果使用 `always` 策略，想永久停止容器需要：

```bash
# 方法 1：先修改策略再停止
docker update --restart=no milvus-attu
docker stop milvus-attu

# 方法 2：停止并删除容器
docker stop milvus-attu
docker rm milvus-attu
```

### 实际测试演示

```bash
# 1. 创建两个测试容器
docker run -d --name test-unless --restart unless-stopped alpine sleep 3600
docker run -d --name test-always --restart always alpine sleep 3600

# 2. 手动停止两个容器
docker stop test-unless test-always

# 3. 查看容器状态（都停止了）
docker ps -a | grep test-

# 4. 重启 Docker 服务
sudo systemctl restart docker

# 5. 查看哪个容器自动启动了
docker ps | grep test-
# test-always 会启动 ✓
# test-unless 不会启动 ✗

# 6. 清理测试容器
docker rm -f test-unless test-always
```

### 其他重启策略

| 策略 | 说明 |
|------|------|
| `no` | 不自动重启（默认） |
| `on-failure` | 只在退出代码非 0 时重启 |
| `on-failure:3` | 最多重试 3 次 |
| `unless-stopped` | 除非手动停止（推荐） |
| `always` | 总是重启 |

### `on-failure` vs `unless-stopped`

```yaml
restart: on-failure
```

**区别：**
- `on-failure` 只在容器**异常退出**（退出码非 0）时重启
- `unless-stopped` 在任何退出情况下都重启（除非手动停止）

**示例：**
```bash
# 容器正常退出（exit 0）
docker run --restart on-failure alpine echo "done"
# 不会重启 ✓

# 容器异常退出（exit 1）
docker run --restart on-failure alpine sh -c "exit 1"
# 会重启 ✓
```

### 最佳实践建议

#### 对于 Milvus 这类生产服务：

```yaml
restart: unless-stopped  # 推荐
```

**理由：**
1. ✅ 虚拟机重启后自动启动
2. ✅ 容器崩溃后自动恢复
3. ✅ 维护时手动停止，不会意外重启
4. ✅ 符合运维习惯

#### 使用场景对比

| 场景 | 推荐策略 |
|------|----------|
| 生产环境服务 | `unless-stopped` |
| 开发测试环境 | `unless-stopped` |
| 关键基础设施 | `unless-stopped` |
| 临时任务容器 | `no` |
| 需要确保运行的监控容器 | `always` |
| CI/CD 构建容器 | `no` 或 `on-failure` |

### 验证当前容器的重启策略

```bash
# 查看所有容器的重启策略
docker inspect --format='{{.Name}} - {{.HostConfig.RestartPolicy.Name}}' $(docker ps -aq)

# 查看单个容器
docker inspect milvus-attu --format='{{.HostConfig.RestartPolicy.Name}}'

# 查看详细的重启策略信息
docker inspect milvus-attu --format='{{json .HostConfig.RestartPolicy}}' | jq
```

### 总结

- **`unless-stopped`**：更灵活，给你控制权（推荐用于生产）
- **`always`**：更激进，保证运行（适合关键监控服务）

**对于您的 Milvus 服务，建议使用 `unless-stopped`**，这样既能在虚拟机重启后自动启动，又能在维护时通过 `docker stop` 正常停止服务。

### ref
[https://chat.deepseek.com/share/srir714f38ux5tlwzo]()