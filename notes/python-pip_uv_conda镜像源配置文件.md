## pip
[pip.ini](%APPDATA%\pip\pip.ini)
```ini
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
extra-index-url = 
	https://mirrors.aliyun.com/pypi/simple
	https://pypi.mirrors.ustc.edu.cn/simple
timeout = 120

[install]
trusted-host = mirrors.aliyun.com
```

## uv
[uv.toml](%APPDATA%\uv\uv.toml)
```toml
# 清华镜像（推荐）
index-url = "https://pypi.tuna.tsinghua.edu.cn/simple"
python-install-mirror = "https://mirror.nju.edu.cn/github-release/astral-sh/python-build-standalone/"
```

## conda
[.condarc](%USERPROFILE%\.condarc)
```yml
# .condarc
channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
  - defaults

show_channel_urls: true
ssl_verify: true

# 其他可选配置（加速）
remote_read_timeout_secs: 30
remote_connect_timeout_secs: 10
auto_activate: false
```
