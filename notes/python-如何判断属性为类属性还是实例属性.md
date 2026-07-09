这是一个非常经典且实用的问题。**判断一个属性是类属性还是实例属性，核心在于查看它属于“类”还是属于“实例”。**

**直接答案：**
1. **类属性**：定义在类体中，**被类的所有实例共享**。可以通过 `ClassName.attr` 或 `self.__class__.attr` 访问。
2. **实例属性**：定义在 `__init__` 方法中或通过 `self.attr = value` 动态添加，**仅属于特定实例**。

**判断方法**：
- 用 `hasattr(instance, 'attr')` 和 `hasattr(Class, 'attr')` 对比。
- 用 `instance.__dict__` 和 `Class.__dict__` 查看存储位置。
- 用 `getattr()` 和 `dir()` 辅助判断。

---

## 1. 快速区分：存储位置

| 存储位置 | 属性类型 |
|----------|----------|
| `instance.__dict__` | 实例属性 |
| `Class.__dict__` | 类属性（包括方法、`__doc__` 等） |

**示例**：
```python
class Person:
    species = "Homo sapiens"  # 类属性
    
    def __init__(self, name):
        self.name = name      # 实例属性

p = Person("Alice")

# 1. 查看存储位置
print(p.__dict__)           # {'name': 'Alice'} → 实例属性
print(Person.__dict__)      # 包含 'species' → 类属性

# 2. 直接判断
print('name' in p.__dict__)     # True → 实例属性
print('species' in Person.__dict__)  # True → 类属性
```

---

## 2. 判断方法详解

### 方法 1：通过 `__dict__` 检查（最直接）

```python
def is_instance_attr(obj, attr_name):
    """判断 attr_name 是否是 obj 的实例属性"""
    return attr_name in obj.__dict__

def is_class_attr(cls, attr_name):
    """判断 attr_name 是否是 cls 的类属性"""
    return attr_name in cls.__dict__

# 使用
p = Person("Alice")
print(is_instance_attr(p, 'name'))     # True
print(is_instance_attr(p, 'species'))  # False
print(is_class_attr(Person, 'species')) # True
```

**局限**：
- 如果类使用了 `__slots__`，实例没有 `__dict__`，需要额外处理。
- 只检查直接定义的属性，不检查继承链。

### 方法 2：通过 `hasattr` + `__dict__` 组合（推荐）

```python
def attr_type(obj, attr_name):
    """判断属性属于类还是实例，或继承而来"""
    if attr_name in obj.__dict__:
        return "实例属性"
    elif hasattr(obj.__class__, attr_name):
        return "类属性"
    else:
        return "不存在"

class Animal:
    kingdom = "Animalia"
    
class Person(Animal):
    species = "Homo sapiens"
    def __init__(self, name):
        self.name = name

p = Person("Alice")
print(attr_type(p, 'name'))     # 实例属性
print(attr_type(p, 'species'))  # 类属性
print(attr_type(p, 'kingdom'))  # 类属性（继承自父类）
print(attr_type(p, 'age'))      # 不存在
```

**注意**：对于继承的类属性，`p.__dict__` 中没有，但 `hasattr(p.__class__, attr_name)` 可以找到。

### 方法 3：通过 `inspect` 模块（更通用）

```python
import inspect

def get_attr_owner(obj, attr_name):
    """返回属性所属的类（如果存在）"""
    if hasattr(obj, attr_name):
        # 检查实例属性
        if attr_name in obj.__dict__:
            return "实例属性"
        # 检查类及其父类
        for cls in inspect.getmro(obj.__class__):
            if attr_name in cls.__dict__:
                return f"类属性（定义在 {cls.__name__}）"
    return "不存在"

print(get_attr_owner(p, 'name'))      # 实例属性
print(get_attr_owner(p, 'species'))   # 类属性（定义在 Person）
print(get_attr_owner(p, 'kingdom'))   # 类属性（定义在 Animal）
```

---

## 3. 特别情况处理

### 3.1 使用 `__slots__` 的类

如果没有 `__dict__`，需要用 `__slots__` 检查：

```python
class Person:
    __slots__ = ('name',)
    species = "Homo sapiens"
    
    def __init__(self, name):
        self.name = name

p = Person("Alice")

# ❌ p.__dict__ 不存在
# print(p.__dict__)  # AttributeError

# ✅ 改用 __slots__
def is_slot_attr(obj, attr_name):
    return hasattr(obj, attr_name) and attr_name in getattr(obj.__class__, '__slots__', ())

print(is_slot_attr(p, 'name'))      # True（实例属性）
print('species' in Person.__dict__) # True（类属性）
```

### 3.2 `@property` 装饰的属性

`@property` 是**描述符（descriptor）**，属于类属性，但访问时像实例属性：

```python
class Person:
    def __init__(self, name):
        self._name = name
    
    @property
    def name(self):
        return self._name

p = Person("Alice")

# 判断：name 是类属性（定义在类中）
print('name' in Person.__dict__)  # True
print('name' in p.__dict__)       # False（p.__dict__ 中只有 _name）
```

### 3.3 动态添加的属性

实例可以在运行时动态添加属性，它们也会出现在 `__dict__` 中：

```python
p = Person("Alice")
p.age = 30  # 动态添加实例属性
print('age' in p.__dict__)  # True
```

---

## 4. 生产级工具函数

```python
from typing import Any, Union

def classify_attribute(obj: Any, attr_name: str) -> dict[str, Union[str, bool]]:
    """
    分类属性并返回详细信息
    
    Returns:
        {
            "exists": bool,
            "type": "instance" | "class" | "inherited" | "property" | "slot",
            "owner": str,
            "value": Any
        }
    """
    result = {"exists": False, "type": None, "owner": None, "value": None}
    
    if not hasattr(obj, attr_name):
        return result
    
    result["exists"] = True
    result["value"] = getattr(obj, attr_name)
    
    # 1. 检查 __slots__
    slots = getattr(obj.__class__, '__slots__', ())
    if attr_name in slots:
        result["type"] = "slot"
        result["owner"] = obj.__class__.__name__
        return result
    
    # 2. 检查实例 __dict__
    if hasattr(obj, '__dict__') and attr_name in obj.__dict__:
        result["type"] = "instance"
        result["owner"] = "instance"
        return result
    
    # 3. 检查类及其父类
    for cls in obj.__class__.__mro__:
        if attr_name in cls.__dict__:
            result["type"] = "class" if cls is obj.__class__ else "inherited"
            result["owner"] = cls.__name__
            # 检查是否为 property
            if isinstance(cls.__dict__[attr_name], property):
                result["type"] = "property"
            return result
    
    return result

# 测试
class Animal:
    kingdom = "Animalia"

class Person(Animal):
    __slots__ = ('_name',)
    species = "Homo sapiens"
    
    def __init__(self, name):
        self._name = name
    
    @property
    def name(self):
        return self._name

p = Person("Alice")
p.age = 30

print(classify_attribute(p, '_name'))   # {'exists': True, 'type': 'slot', 'owner': 'Person', ...}
print(classify_attribute(p, 'name'))    # {'exists': True, 'type': 'property', 'owner': 'Person', ...}
print(classify_attribute(p, 'species')) # {'exists': True, 'type': 'class', 'owner': 'Person', ...}
print(classify_attribute(p, 'kingdom')) # {'exists': True, 'type': 'inherited', 'owner': 'Animal', ...}
print(classify_attribute(p, 'age'))     # {'exists': True, 'type': 'instance', 'owner': 'instance', ...}
```

---

## 5. 总结对比表

| 属性类型 | 定义位置 | 存储位置 | 访问方式 | 判断方法 |
|----------|----------|----------|----------|----------|
| **类属性** | 类体中 | `Class.__dict__` | `Class.attr` 或 `instance.attr` | `attr in Class.__dict__` |
| **实例属性** | `__init__` 或 `self.attr =` | `instance.__dict__` | `instance.attr` | `attr in instance.__dict__` |
| **继承的类属性** | 父类中 | `Parent.__dict__` | `instance.attr` | `attr in Parent.__dict__` |
| **`__slots__` 属性** | `__slots__` 中 | 无 `__dict__` | `instance.attr` | `attr in Class.__slots__` |
| **`@property`** | 类体中 | `Class.__dict__`（描述符） | `instance.attr`（调用 getter） | `isinstance(Class.__dict__[attr], property)` |
| **动态添加属性** | 运行时 | `instance.__dict__` | `instance.attr` | `attr in instance.__dict__` |

---

**一句话总结**：
> **判断类属性还是实例属性，最直接的方法是检查 `attr in obj.__dict__`（实例属性）和 `attr in obj.__class__.__dict__`（类属性）。注意 `__slots__`、`@property`、继承链等特殊情况，生产环境中可以使用封装好的工具函数统一处理。**


### ref
[https://chat.deepseek.com/share/17tdh7wcq9ov9mz9px]()