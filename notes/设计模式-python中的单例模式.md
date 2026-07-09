单例模式（Singleton）是确保一个类**只有一个实例**的设计模式。Python 中实现单例的方式有很多，各有优劣。

---

## 1. 为什么需要单例模式？

**适用场景**：
- 配置管理器（`ConfigManager`）
- 数据库连接池
- 日志记录器（`Logger`）
- 缓存管理器
- 线程池
- 全局状态管理器

**核心目标**：
- 确保全局只有一个实例
- 提供全局访问点
- 避免重复创建资源密集型对象

---

## 2. Python 中的实现方式（由简到繁）

### 方式 1：模块级全局变量（最推荐，最简单）

Python 模块本身就是天然的单例（模块在首次导入时被初始化，且只初始化一次）。

```python
# config.py
class Config:
    def __init__(self):
        self.app_name = "MyApp"
        self.debug = True

# 创建全局唯一实例
config = Config()

# use_config.py
from config import config

print(config.app_name)  # MyApp
```

**优点**：
- 实现最简单，无需额外代码
- 线程安全（Python 模块导入是线程安全的）
- 符合 Python 习惯（Pythonic）

**缺点**：
- 无法延迟初始化（模块导入时就创建）
- 难以控制实例化过程

---

### 方式 2：使用 `__new__`（经典方式）

通过重写 `__new__` 控制实例创建。

```python
class Singleton:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 注意：__init__ 每次都会调用！
        # 需要避免重复初始化
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.value = 0

# 测试
s1 = Singleton()
s2 = Singleton()
print(s1 is s2)  # True
```

**优点**：
- 经典实现，容易被理解
- 可以控制实例化过程

**缺点**：
- `__init__` 每次都会执行，需要手动标记初始化状态
- 继承时需要额外处理

**改进版：线程安全**

```python
import threading

class Singleton:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # 双重检查
                    cls._instance = super().__new__(cls)
        return cls._instance
```

---

### 方式 3：使用装饰器（优雅）

```python
def singleton(cls):
    instances = {}
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

# 使用
@singleton
class Database:
    def __init__(self):
        self.connection = "Connected"
        print("创建数据库连接")

db1 = Database()
db2 = Database()
print(db1 is db2)  # True
```

**优点**：
- 代码简洁，可复用
- 可以装饰任何类

**缺点**：
- 装饰后类变成了函数，`isinstance(db1, Database)` 返回 `False`
- 无法使用类方法（`@classmethod`）
- 不支持继承

---

### 方式 4：使用元类（Metaclass）

```python
class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]

# 使用
class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.connection = "Connected"
        print("创建数据库连接")

db1 = Database()
db2 = Database()
print(db1 is db2)  # True
print(isinstance(db1, Database))  # True
```

**优点**：
- 最完整的实现，支持继承
- 保留 `isinstance` 检查
- 支持类方法

**缺点**：
- 理解门槛较高（元类）
- 代码相对复杂

---

### 方式 5：使用 `functools.lru_cache`（特殊技巧）

```python
from functools import lru_cache

class Config:
    def __init__(self, env="development"):
        self.env = env
        self.settings = {"host": "localhost"}

@lru_cache(maxsize=1)
def get_config(env="development"):
    return Config(env)

# 使用
config1 = get_config()
config2 = get_config()
print(config1 is config2)  # True
```

**优点**：
- 利用缓存机制自动实现单例
- 支持带参数的单例（不同参数返回不同实例）

**缺点**：
- 只能用于函数，不能直接用于类
- 需要额外的函数包装

---

### 方式 6：使用 `dataclass` + `__new__`

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Singleton:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.value = 0

s1 = Singleton()
s2 = Singleton()
print(s1 is s2)  # True
```

---

## 3. 各种方式的对比总结

| 方式 | 线程安全 | 支持继承 | 延迟加载 | 代码复杂度 | 推荐度 |
|------|---------|---------|---------|-----------|--------|
| **模块全局变量** | ✅ | ✅ | ❌ | ⭐ | ⭐⭐⭐⭐⭐ |
| **`__new__`** | ✅（需加锁） | ⚠️ 需处理 | ✅ | ⭐⭐ | ⭐⭐⭐⭐ |
| **装饰器** | ✅ | ❌ | ✅ | ⭐⭐ | ⭐⭐⭐ |
| **元类** | ✅ | ✅ | ✅ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **`lru_cache`** | ✅ | ❌ | ✅ | ⭐⭐ | ⭐⭐⭐ |
| **`dataclass` + `__new__`** | ✅ | ⚠️ 需处理 | ✅ | ⭐⭐⭐ | ⭐⭐⭐ |

---

## 4. 实际项目中的最佳实践

### 推荐：模块全局变量 + 工厂函数

```python
# database.py
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

class Database:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=True)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)
    
    async def get_session(self) -> AsyncSession:
        return self.async_session()

# 全局单例实例（模块导入时创建）
_db_instance = None

def get_database(database_url: str | None = None) -> Database:
    """工厂函数：返回单例数据库实例（支持延迟初始化）"""
    global _db_instance
    if _db_instance is None:
        if database_url is None:
            raise ValueError("Database URL must be provided for first initialization")
        _db_instance = Database(database_url)
    return _db_instance

# 在 FastAPI 项目中使用
from app.core.config import settings

# 启动时初始化
db = get_database(settings.DATABASE_URL)

@app.on_event("startup")
async def startup():
    global db
    db = get_database(settings.DATABASE_URL)
```

### 推荐：使用元类实现通用单例基类

```python
import threading
from typing import Type, TypeVar, Dict

T = TypeVar('T', bound='SingletonMeta')

class SingletonMeta(type):
    """线程安全的单例元类"""
    _instances: Dict[Type, object] = {}
    _lock: threading.Lock = threading.Lock()
    
    def __call__(cls: Type[T], *args, **kwargs) -> T:
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]

# 使用：继承即可获得单例能力
class ConfigManager(metaclass=SingletonMeta):
    def __init__(self):
        self.config = {}
    
    def set(self, key, value):
        self.config[key] = value
    
    def get(self, key):
        return self.config.get(key)

# 任何地方使用都是同一个实例
config1 = ConfigManager()
config2 = ConfigManager()
print(config1 is config2)  # True
```

---

## 5. 反模式：不要这样写单例

```python
# ❌ 不推荐：使用类变量 + __init__ 判断
class Singleton:
    _instance = None
    
    def __init__(self):
        if self._instance is None:
            self._instance = self
# 问题：__init__ 每次都会被调用，逻辑混乱


# ❌ 不推荐：使用全局变量
class _Config:
    pass

config = _Config()  # 全局变量，失去了类的封装性
```

---

## 6. 模块全局变量 vs 元类：何时选哪个？

| 场景 | 推荐方式 |
|------|----------|
| **简单应用**（如配置、日志） | 模块全局变量 |
| **需要延迟初始化**（如数据库连接） | 模块全局变量 + 工厂函数 |
| **需要继承和多态**（如插件系统） | 元类 |
| **需要控制实例创建过程**（如缓存策略） | `__new__` |
| **库/框架开发**（用户使用你的类） | 元类（用户无感知） |
| **单测/ mock** | 模块全局变量（容易替换） |

---

**一句话总结**：
> **Python 中最推荐的单例模式是“模块全局变量”（天然单例），简单且线程安全。如果需要延迟初始化，用工厂函数包装。如果必须控制类实例化过程（如框架开发），用元类实现。避免在 `__init__` 中做单例判断，这会让代码难以理解和维护。**


### ref
[https://chat.deepseek.com/share/ydwcmvmms47e447pek]()