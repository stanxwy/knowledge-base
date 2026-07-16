## 一句话总结（CentOS 时间同步黄金流程）
```bash
# 安装/确认 chrony
sudo yum/dnf install -y chrony

# 启动服务
sudo systemctl enable --now chronyd

# 立即强制同步（时间差大时必须）
sudo chronyc -a makestep

# 设时区
sudo timedatectl set-timezone Asia/Shanghai

# 查看状态
timedatectl status
chronyc sources -v
```

## 创建 MinIO 连接时报错
```bash
2026-07-16 14:32:16 - minio_utils.py:41 - ERROR - Minio init failed:S3 operation failed; code: RequestTimeTooSkewed, message: The difference between the request time and the server's time is too large., resource: /knowledge-base, request_id: 18C28FAFBE3BE426, host_id: dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8
```
S3 / MinIO 强制校验请求时间戳，防止重放攻击。
默认阈值一般是：`±15 分钟`
只要两端时间差超过这个值，直接拒绝请求。

## 查看本地 CentOS 服务器当前时间
```bash
[root@localhost ~]# date +"%F %T"
2026-07-15 16:15:41
```

## 检查 chronyd 是否安装
```bash
[root@localhost ~]# rpm -qa | grep chrony
chrony-3.4-1.el7.x86_64
```

## 启动并设置开机自启 chronyd
```bash
[root@localhost ~]# sudo systemctl enable chronyd
[root@localhost ~]# sudo systemctl start chronyd

[root@localhost ~]# systemctl status chronyd
● chronyd.service - NTP client/server
   Loaded: loaded (/usr/lib/systemd/system/chronyd.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2026-07-14 20:24:25 EDT; 19h ago
     Docs: man:chronyd(8)
           man:chrony.conf(5)
 Main PID: 698 (chronyd)
   CGroup: /system.slice/chronyd.service
           └─698 /usr/sbin/chronyd

Jul 14 20:24:31 localhost.localdomain chronyd[698]: System clock wrong by 1536.106340 seconds, adjustment started
Jul 14 20:50:07 localhost.localdomain chronyd[698]: System clock was stepped by 1536.106340 seconds
Jul 14 20:52:26 localhost.localdomain chronyd[698]: Source 193.182.111.142 replaced with 139.199.215.251
Jul 14 21:02:00 localhost.localdomain chronyd[698]: Selected source 111.230.189.174
Jul 15 05:53:56 localhost.localdomain chronyd[698]: Selected source 139.199.215.251
Jul 15 09:24:07 localhost.localdomain chronyd[698]: Selected source 111.230.189.174
Jul 15 09:25:11 localhost.localdomain chronyd[698]: Source 139.199.215.251 replaced with 119.28.206.193
Jul 15 09:39:15 localhost.localdomain chronyd[698]: Selected source 119.28.206.193
Jul 15 09:39:15 localhost.localdomain chronyd[698]: System clock wrong by 38965.791074 seconds, adjustment started
Jul 15 10:21:00 localhost.localdomain chronyd[698]: Selected source 111.230.189.174
```

## 手动立即同步一次
```bash
[root@localhost ~]# sudo chronyc -a makestep
200 OK
```

## 查看时间同步状态
重点看：  
- *表示当前正在使用的同步源
- +表示候选源
- 最后一列有 offset，单位毫秒
```bash
[root@localhost ~]# chronyc sources -v
210 Number of sources = 4

  .-- Source mode  '^' = server, '=' = peer, '#' = local clock.
 / .- Source state '*' = current synced, '+' = combined , '-' = not combined,
| /   '?' = unreachable, 'x' = time may be in error, '~' = time too variable.
||                                                 .- xxxx [ yyyy ] +/- zzzz
||      Reachability register (octal) -.           |  xxxx = adjusted offset,
||      Log2(Polling interval) --.      |          |  yyyy = measured offset,
||                                \     |          |  zzzz = estimated error.
||                                 |    |           \
MS Name/IP address         Stratum Poll Reach LastRx Last sample
===============================================================================
^* 111.230.189.174               2  10   377   396   -965us[-1156us] +/-   44ms
^- tock.ntp.infomaniak.ch        1  10   357   203  -1893us[-1893us] +/-  106ms
^+ 119.28.206.193                2  10   377   470  -2372us[-2563us] +/-   44ms
^+ 119.28.183.184                2  10   377   312   -592us[ -592us] +/-   34ms
```

## 再看同步是否生效：
确认这两项是 yes：  
- System clock synchronized: yes
- NTP service: active
```bash
[root@localhost ~]# timedatectl status
      Local time: Thu 2026-07-16 02:36:22 EDT
  Universal time: Thu 2026-07-16 06:36:22 UTC
        RTC time: Wed 2026-07-15 19:46:56
       Time zone: America/New_York (EDT, -0400)
     NTP enabled: yes
NTP synchronized: no
 RTC in local TZ: no
      DST active: yes
 Last DST change: DST began at
                  Sun 2026-03-08 01:59:59 EST
                  Sun 2026-03-08 03:00:00 EDT
 Next DST change: DST ends (the clock jumps one hour backwards) at
                  Sun 2026-11-01 01:59:59 EDT
                  Sun 2026-11-01 01:00:00 EST
```

## 查看当前时区
```bash
[root@localhost ~]# timedatectl
      Local time: Thu 2026-07-16 02:36:43 EDT
  Universal time: Thu 2026-07-16 06:36:43 UTC
        RTC time: Wed 2026-07-15 19:47:17
       Time zone: America/New_York (EDT, -0400)
     NTP enabled: yes
NTP synchronized: no
 RTC in local TZ: no
      DST active: yes
 Last DST change: DST began at
                  Sun 2026-03-08 01:59:59 EST
                  Sun 2026-03-08 03:00:00 EDT
 Next DST change: DST ends (the clock jumps one hour backwards) at
                  Sun 2026-11-01 01:59:59 EDT
                  Sun 2026-11-01 01:00:00 EST
```

## 再次查看本地时间
```bash
[root@localhost ~]# date +"%F %T"
2026-07-16 02:37:10
```

## 防火墙 / 网络检查（同步失败常见原因）
```bash
# NTP 用 UDP 123，确保没被拦：
sudo firewall-cmd --list-ports
# 需要的话：
sudo firewall-cmd --add-port=123/udp --permanent
sudo firewall-cmd --reload

# 如果是云服务器（阿里云 / 腾讯云 / AWS）：
# 安全组也要放行 UDP 123
# 或者用云厂商提供的 NTP 源
```

## 修改 NTP 源（国内服务器推荐）
```bash
# 编辑：
sudo vi /etc/chrony.conf

# 把 server 改成国内源，例如：
server ntp.aliyun.com iburst
server cn.pool.ntp.org iburst
server time.google.com iburst

# 重启生效：
sudo systemctl restart chronyd
sudo chronyc -a makestep
```

