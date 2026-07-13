## set security policy in powershell
```bash
PS D:\> Set-ExecutionPolicy Unrestricted -Scope CurrentUser
```

## create uv directory
```bash
PS D:\> mkdir -Force $env:APPDATA\uv


    Directory: C:\Users\stan\AppData\Roaming


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----        13/07/2026  10:45 AM                uv
```

## create uv.toml
```bash
PS D:\> New-Item -Path $env:APPDATA\uv\uv.toml -ItemType File


    Directory: C:\Users\stan\AppData\Roaming\uv


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----        13/07/2026  10:46 AM              0 uv.toml
```

## set mirror repo in uv.toml
- %APPDATA%\uv\uv.toml
```bash
# 清华镜像（推荐）
index-url = "https://pypi.tuna.tsinghua.edu.cn/simple"
python-install-mirror = "https://mirror.nju.edu.cn/github-release/astral-sh/python-build-standalone/"
```

## list installed python versions
```bash
PS D:\> uv python list
cpython-3.14.0rc2-windows-x86_64-none                 <download available>
cpython-3.14.0rc2+freethreaded-windows-x86_64-none    <download available>
cpython-3.13.13-windows-x86_64-none                   D:\dev\miniconda3\python.exe
cpython-3.13.7-windows-x86_64-none                    <download available>
cpython-3.13.7+freethreaded-windows-x86_64-none       <download available>
cpython-3.13.3-windows-x86_64-none                    C:\Users\stan\AppData\Local\Programs\Python\Python313\python.exe
cpython-3.12.11-windows-x86_64-none                   <download available>
cpython-3.11.13-windows-x86_64-none                   <download available>
cpython-3.10.18-windows-x86_64-none                   <download available>
cpython-3.9.23-windows-x86_64-none                    <download available>
cpython-3.8.20-windows-x86_64-none                    <download available>
pypy-3.11.13-windows-x86_64-none                      <download available>
pypy-3.10.16-windows-x86_64-none                      <download available>
pypy-3.9.19-windows-x86_64-none                       <download available>
pypy-3.8.16-windows-x86_64-none                       <download available>
graalpy-3.11.0-windows-x86_64-none                    <download available>
graalpy-3.10.0-windows-x86_64-none                    <download available>
```

## install python 3.11
```bash
PS D:\> uv python install 3.11
Installed Python 3.11.13 in 12.39s
 + cpython-3.11.13-windows-x86_64-none (python3.11.exe)

PS D:\> uv python list
cpython-3.14.0rc2-windows-x86_64-none                 <download available>
cpython-3.14.0rc2+freethreaded-windows-x86_64-none    <download available>
cpython-3.13.13-windows-x86_64-none                   D:\dev\miniconda3\python.exe
cpython-3.13.7-windows-x86_64-none                    <download available>
cpython-3.13.7+freethreaded-windows-x86_64-none       <download available>
cpython-3.13.3-windows-x86_64-none                    C:\Users\stan\AppData\Local\Programs\Python\Python313\python.exe
cpython-3.12.11-windows-x86_64-none                   <download available>
cpython-3.11.13-windows-x86_64-none                   C:\Users\stan\AppData\Roaming\uv\python\cpython-3.11.13-windows-x86_64-none\python.exe
cpython-3.11.13-windows-x86_64-none                   C:\Users\stan\.local\bin\python3.11.exe
cpython-3.11.13-windows-x86_64-none                   <download available>
cpython-3.10.18-windows-x86_64-none                   <download available>
cpython-3.9.23-windows-x86_64-none                    <download available>
cpython-3.8.20-windows-x86_64-none                    <download available>
pypy-3.11.13-windows-x86_64-none                      <download available>
pypy-3.10.16-windows-x86_64-none                      <download available>
pypy-3.9.19-windows-x86_64-none                       <download available>
pypy-3.8.16-windows-x86_64-none                       <download available>
graalpy-3.11.0-windows-x86_64-none                    <download available>
graalpy-3.10.0-windows-x86_64-none                    <download available>
```

## create and activate venv for project
```bash
PS D:\knowledge-base> uv venv --python 3.11
Using CPython 3.11.13
Creating virtual environment at: .venv
Activate with: .venv\Scripts\activate
PS D:\knowledge-base> .venv\Scripts\activate
```

## install dependencies
```bash
(knowledge-base) PS D:\knowledge-base> uv add python-dotenv
Resolved 2 packages in 1.12s
Prepared 1 package in 237ms
░░░░░░░░░░░░░░░░░░░░ [0/1] Installing wheels...                                                                                                                                                                  warning: Failed to hardlink files; falling back to full copy. This may lead to degraded performance.
         If the cache and target directories are on different filesystems, hardlinking may not be supported.
         If this is intentional, set `export UV_LINK_MODE=copy` or use `--link-mode=copy` to suppress this warning.
Installed 1 package in 26ms
 + python-dotenv==1.2.2

(knowledge-base) PS D:\knowledge-base> uv add python-dotenv numpy langgraph grandalf fastapi minio langchain-openai langchain langchain-text-splitters pymongo colorlog
Resolved 62 packages in 15.48s
Prepared 59 packages in 13.70s
░░░░░░░░░░░░░░░░░░░░ [0/59] Installing wheels...                                                                                                                                                                 warning: Failed to hardlink files; falling back to full copy. This may lead to degraded performance.
         If the cache and target directories are on different filesystems, hardlinking may not be supported.
         If this is intentional, set `export UV_LINK_MODE=copy` or use `--link-mode=copy` to suppress this warning.
Installed 59 packages in 2.04s
 + annotated-doc==0.0.4
 + annotated-types==0.7.0
 + anyio==4.14.2
 + argon2-cffi==25.1.0
 + argon2-cffi-bindings==25.1.0
 + certifi==2026.6.17
 + cffi==2.1.0
 + charset-normalizer==3.4.9
 + colorama==0.4.6
 + colorlog==6.10.1
 + distro==1.9.0
 + dnspython==2.8.0
 + fastapi==0.139.0
 + grandalf==0.8
 + h11==0.16.0
 + httpcore==1.0.9
 + httpx==0.28.1
 + idna==3.18
 + jiter==0.16.0
 + jsonpatch==1.33
 + jsonpointer==3.1.1
 + langchain==1.3.13
 + langchain-core==1.4.9
 + langchain-openai==1.3.5
 + langchain-protocol==0.0.18
 + langchain-text-splitters==1.1.2
 + langgraph==1.2.9
 + langgraph-checkpoint==4.1.1
 + langgraph-prebuilt==1.1.0
 + langgraph-sdk==0.4.2
 + langsmith==0.10.2
 + minio==7.2.20
 + numpy==2.4.6
 + openai==2.45.0
 + orjson==3.11.9
 + ormsgpack==1.12.2
 + packaging==26.2
 + pycparser==3.0
 + pycryptodome==3.23.0
 + pydantic==2.13.4
 + pydantic-core==2.46.4
 + pymongo==4.17.0
 + pyparsing==3.3.2
 + pyyaml==6.0.3
 + regex==2026.7.10
 + requests==2.34.2
 + requests-toolbelt==1.0.0
 + sniffio==1.3.1
 + starlette==1.3.1
 + tenacity==9.1.4
 + tiktoken==0.13.0
 + tqdm==4.68.4
 + typing-extensions==4.16.0
 + typing-inspection==0.4.2
 + urllib3==2.7.0
 + uuid-utils==0.17.0
 + websockets==15.0.1
 + xxhash==3.8.1
 + zstandard==0.25.0
```

## show installed packages
```bash
(knowledge-base) PS D:\knowledge-base> uv tree
Resolved 62 packages in 1ms
knowledge-base v0.1.0
├── colorlog v6.10.1
│   └── colorama v0.4.6
├── fastapi v0.139.0
│   ├── annotated-doc v0.0.4
│   ├── pydantic v2.13.4
│   │   ├── annotated-types v0.7.0
│   │   ├── pydantic-core v2.46.4
│   │   │   └── typing-extensions v4.16.0
│   │   ├── typing-extensions v4.16.0
│   │   └── typing-inspection v0.4.2
│   │       └── typing-extensions v4.16.0
│   ├── starlette v1.3.1
│   │   ├── anyio v4.14.2
│   │   │   ├── idna v3.18
│   │   │   └── typing-extensions v4.16.0
│   │   └── typing-extensions v4.16.0
│   ├── typing-extensions v4.16.0
│   └── typing-inspection v0.4.2 (*)
├── grandalf v0.8
│   └── pyparsing v3.3.2
├── langchain v1.3.13
│   ├── langchain-core v1.4.9
│   │   ├── jsonpatch v1.33
│   │   │   └── jsonpointer v3.1.1
│   │   ├── langchain-protocol v0.0.18
│   │   │   └── typing-extensions v4.16.0
│   │   ├── langsmith v0.10.2
│   │   │   ├── anyio v4.14.2 (*)
│   │   │   ├── distro v1.9.0
│   │   │   ├── httpx v0.28.1
│   │   │   │   ├── anyio v4.14.2 (*)
│   │   │   │   ├── certifi v2026.6.17
│   │   │   │   ├── httpcore v1.0.9
│   │   │   │   │   ├── certifi v2026.6.17
│   │   │   │   │   └── h11 v0.16.0
│   │   │   │   └── idna v3.18
│   │   │   ├── orjson v3.11.9
│   │   │   ├── packaging v26.2
│   │   │   ├── pydantic v2.13.4 (*)
│   │   │   ├── requests v2.34.2
│   │   │   │   ├── certifi v2026.6.17
│   │   │   │   ├── charset-normalizer v3.4.9
│   │   │   │   ├── idna v3.18
│   │   │   │   └── urllib3 v2.7.0
│   │   │   ├── requests-toolbelt v1.0.0
│   │   │   │   └── requests v2.34.2 (*)
│   │   │   ├── sniffio v1.3.1
│   │   │   ├── typing-extensions v4.16.0
│   │   │   ├── uuid-utils v0.17.0
│   │   │   ├── websockets v15.0.1
│   │   │   ├── xxhash v3.8.1
│   │   │   └── zstandard v0.25.0
│   │   ├── packaging v26.2
│   │   ├── pydantic v2.13.4 (*)
│   │   ├── pyyaml v6.0.3
│   │   ├── tenacity v9.1.4
│   │   ├── typing-extensions v4.16.0
│   │   └── uuid-utils v0.17.0
│   ├── langgraph v1.2.9
│   │   ├── langchain-core v1.4.9 (*)
│   │   ├── langgraph-checkpoint v4.1.1
│   │   │   ├── langchain-core v1.4.9 (*)
│   │   │   └── ormsgpack v1.12.2
│   │   ├── langgraph-prebuilt v1.1.0
│   │   │   ├── langchain-core v1.4.9 (*)
│   │   │   └── langgraph-checkpoint v4.1.1 (*)
│   │   ├── langgraph-sdk v0.4.2
│   │   │   ├── httpx v0.28.1 (*)
│   │   │   ├── langchain-core v1.4.9 (*)
│   │   │   ├── langchain-protocol v0.0.18 (*)
│   │   │   ├── orjson v3.11.9
│   │   │   └── websockets v15.0.1
│   │   ├── pydantic v2.13.4 (*)
│   │   └── xxhash v3.8.1
│   └── pydantic v2.13.4 (*)
├── langchain-openai v1.3.5
│   ├── langchain-core v1.4.9 (*)
│   ├── openai v2.45.0
│   │   ├── anyio v4.14.2 (*)
│   │   ├── distro v1.9.0
│   │   ├── httpx v0.28.1 (*)
│   │   ├── jiter v0.16.0
│   │   ├── pydantic v2.13.4 (*)
│   │   ├── sniffio v1.3.1
│   │   ├── tqdm v4.68.4
│   │   │   └── colorama v0.4.6
│   │   └── typing-extensions v4.16.0
│   └── tiktoken v0.13.0
│       ├── regex v2026.7.10
│       └── requests v2.34.2 (*)
├── langchain-text-splitters v1.1.2
│   └── langchain-core v1.4.9 (*)
├── langgraph v1.2.9 (*)
├── minio v7.2.20
│   ├── argon2-cffi v25.1.0
│   │   └── argon2-cffi-bindings v25.1.0
│   │       └── cffi v2.1.0
│   │           └── pycparser v3.0
│   ├── certifi v2026.6.17
│   ├── pycryptodome v3.23.0
│   ├── typing-extensions v4.16.0
│   └── urllib3 v2.7.0
├── numpy v2.4.6
├── pymongo v4.17.0
│   └── dnspython v2.8.0
└── python-dotenv v1.2.2
(*) Package tree already displayed
(knowledge-base) PS D:\knowledge-base>
```