配置 Docker 镜像源（也叫镜像加速器/注册表镜像）主要是为了解决国内访问 Docker Hub 速度慢甚至无法连接的问题。

根据你的使用场景，配置方法分为**包管理器安装源**（解决 `docker-ce` 下载慢）和**容器拉取源**（解决 `docker pull` 下载慢）两种。我猜你大概率是想问后者，但为了全面，我把两者都给你说清楚：

---

### 场景一：配置容器拉取加速器（最常用）
这是指修改 Docker 守护进程的配置，让 `docker pull` 命令自动从国内镜像仓库（如阿里云、中科大、网易）拉取镜像。

**操作步骤（适用于 Linux / Mac / Windows）：**

1. 编辑（或创建）Docker 守护进程配置文件 `/etc/docker/daemon.json`（Windows 下路径为 `C:\ProgramData\docker\config\daemon.json`）：
```bash
sudo vim /etc/docker/daemon.json
```

2. 写入以下内容（这里以**阿里云**为例，速度最稳，但**强烈建议**你去阿里云控制台申请自己的专属加速地址，后面会解释）：
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
```
*（注：中科大 `ustc` 和网易 `163` 是公共加速器，无需注册即可使用）*

3. 重启 Docker 服务使配置生效：
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

4. 验证是否配置成功：
```bash
docker info | grep -A 1 "Registry Mirrors"
```
如果输出了你填写的地址，就说明配置成功了。

---

### ⚠️ 关于阿里云专属加速地址（重要）
如果你用阿里云服务器（ECS），或者免费注册了阿里云账号，建议使用**专属加速地址**，速度比公共镜像快得多。

- 登录阿里云（https://cr.console.aliyun.com/）
- 点击左侧“镜像加速器”，你会得到一个形如 `https://xxxxx.mirror.aliyuncs.com` 的地址
- 把它填进上面 `daemon.json` 的 `registry-mirrors` 数组里（放在第一个位置优先级最高）

---

### 场景二：配置 Docker 软件源（解决安装 docker-ce 慢）
如果你是在用 `yum` 或 `apt` 安装 Docker 本身时速度很慢，需要换国内的软件源。

- **CentOS / RHEL**（更换为阿里云源）：
```bash
sudo yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
sudo yum makecache fast
```

- **Ubuntu / Debian**：
```bash
sudo add-apt-repository "deb [arch=amd64] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
```

---

### 场景三：针对私有仓库或特定镜像单独配置（进阶）
如果你不是要加速所有镜像，而是需要从某个私有仓库（比如公司内网 Harbor）拉取，或者只针对 `gcr.io`、`quay.io` 等特定域名配置代理，可以在 `daemon.json` 中添加 `insecure-registries`（允许 HTTP 访问）或在系统层面配置 HTTP_PROXY 环境变量（适合内网代理拉取）。

---

### 三个容易踩的坑（切记）：
1. **JSON 格式必须严格正确**：不要有多余的逗号，否则 Docker 会启动失败（可以用 JSON 在线校验工具检查）。
2. **不要混用多个加速器**：虽然可以填多个，但 Docker 只会按顺序尝试，**第一个失效才会尝试第二个**，填两个足矣。
3. **国内公共加速器（如中科大）近期对非教育网 IP 有限速**，如果你拉取大型镜像（如 `pytorch/pytorch`）很慢，换成阿里云专属地址通常能解决。

---

如果你告诉我你用的是 **CentOS** 还是 **Ubuntu**，以及是在**公司内网**还是**云服务器**上，我可以给你直接复制粘贴的一条龙命令，省得你手动编辑。

### ref
[https://chat.deepseek.com/share/cin9i8m6jqdwer9abd]()