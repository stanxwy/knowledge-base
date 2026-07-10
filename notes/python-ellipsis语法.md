这是一个非常好的问题，直接触及了 Python 中一个**被严重低估但功能强大的语法符号**。

**直接答案：**
`...`（三个点）在 Python 中是一个**字面量对象**，正式名称为 **`Ellipsis`**（省略号）。它是 Python 内置的一个单例常量，等价于 `Ellipsis`。

它的主要用途包括：
1. **占位符**（未实现的代码）
2. **NumPy 中的切片**（表示“所有维度”）
3. **类型注解中的可变长度元组**（`Tuple[int, ...]`）
4. **动态代码的“我不关心”占位符**

---

## 1. 基本身份：`Ellipsis` 对象

```python
# `...` 是一个内置对象
print(...)              # Ellipsis
print(type(...))        # <class 'ellipsis'>
print(Ellipsis)         # Ellipsis
print(... is Ellipsis)  # True

# 它是一个单例
a = ...
b = ...
print(a is b)  # True
```

---

## 2. 主要用途

### 2.1 占位符（Placeholder）——最常用

在编写代码时，用 `...` 表示“暂未实现”或“以后补充”。

```python
def my_function():
    ...  # 空函数，后续实现

def complex_algorithm():
    ...  # 占位

class MyClass:
    def method(self):
        ...  # 占位
```

**为什么不用 `pass`？**
- `...` 是**表达式**，而 `pass` 是**语句**。
- 在函数体、类体、循环体中都可以用 `...`，更灵活。
- `...` 在某些上下文中比 `pass` 更具语义（“这里有内容，但还没写”）。

```python
# ❌ 不能这样用
result = lambda x: pass  # SyntaxError

# ✅ 可以这样用
result = lambda x: ...   # 可以，表示暂时未实现
```

### 2.2 NumPy 切片：表示“所有维度”（最强大的用法）

在 NumPy 中，`...` 表示“选择所有未被显式索引的维度”。

```python
import numpy as np

# 创建一个 3D 数组 (3, 4, 5)
arr = np.random.rand(3, 4, 5)

# 选择所有第一维，保留后两维所有数据
print(arr[0, ...].shape)   # (4, 5)  → 等价于 arr[0, :, :]

# 选择后两维，保留第一维所有数据
print(arr[..., 0].shape)   # (3, 4)  → 等价于 arr[:, :, 0]

# 同时使用：第一维取索引 1，第三维取索引 2
print(arr[1, ..., 2].shape)  # (4,)  → 等价于 arr[1, :, 2]
```

**为什么会这样设计？**
- 当数组维度很高（如 5D、6D）时，用 `:` 写起来很冗长。
- `...` 自动“展开”为所有未指定的维度，简洁且易读。

```python
# 5D 数组
arr_5d = np.random.rand(2, 3, 4, 5, 6)

# 用冒号写（繁琐）
arr_5d[0, :, :, :, 1]  # 繁琐

# 用省略号写（简洁）
arr_5d[0, ..., 1]      # 等价
```

### 2.3 类型注解：变长元组

在 `typing` 模块中，`...` 表示“任意数量的相同类型元素”。

```python
from typing import Tuple

# 定义一个固定长度元组（3 个 int）
def process_coordinates(coord: Tuple[int, int, int]):
    pass

# 定义一个变长元组（任意数量的 int）
def process_numbers(nums: Tuple[int, ...]):
    pass

# 使用示例
process_numbers((1, 2, 3, 4, 5))  # ✅ 可以
process_numbers((1,))              # ✅ 可以
process_numbers((1, "2"))          # ❌ 类型错误

# 在 Python 3.9+ 中，可以直接用内置 tuple[int, ...]
def process_items(items: tuple[int, ...]):
    pass
```

### 2.4 多参数函数的类型提示

`...` 在 `Callable` 类型中也表示“任意参数”：

```python
from typing import Callable

# 任意参数、任意返回值的函数
def apply(func: Callable[..., int]) -> int:
    return func()

# 也可以指定参数
def apply_two(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

# 使用
apply(lambda: 42)              # ✅
apply(lambda x, y: x + y)      # ❌ 类型检查器报错（预期无参数）
```

### 2.5 在 `functools.partial` 中作为占位符

`...` 可以表示“这个参数稍后填充”：

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

# 固定 exponent，稍后传入 base
square = partial(power, exponent=2)
print(square(5))  # 25

# 在某些场景中，`...` 可用于指示“未绑定”的参数
# （但在标准库中较少使用）
```

### 2.6 在 Pydantic 中表示“未定义”或“任意值”

Pydantic 的高级用法中，`...` 表示“该字段是必需的”：

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int = 18
    email: str = ...  # 这个字段是必须的，没有默认值

# 以下是错误示例
# user = User(name="Alice")  # ❌ email 必须提供

# ✅ 正确
user = User(name="Alice", email="alice@example.com")
```

### 2.7 在异常中表示“当前不是预期值”

某些库的文档中，`...` 用作“当前未定义”的占位符，但这不是标准用法。

---

## 3. 完整用法对比表

| 上下文 | 用法 | 含义 |
|--------|------|------|
| **代码占位** | `def func(): ...` | 暂未实现 |
| **NumPy 切片** | `arr[0, ...]` | 选择所有未指定的维度 |
| **类型注解（Tuple）** | `Tuple[int, ...]` | 任意数量的 int |
| **类型注解（Callable）** | `Callable[..., int]` | 任意参数列表 |
| **Pydantic 模型** | `field: type = ...` | 该字段是必需的 |
| **Lambda** | `lambda x: ...` | 占位表达式 |

---

## 4. 常见误区

### 误区 1：`...` 和 `pass` 完全一样

❌ **不完全一样**：
- `pass` 是**语句**，什么都不做。
- `...` 是**表达式**，求值为 `Ellipsis` 对象。
- 在需要表达式的地方只能用 `...`（如 lambda）。

```python
# ✅ 可以
lambda x: ...

# ❌ 不能
lambda x: pass  # SyntaxError
```

### 误区 2：`...` 只能用于占位

❌ 它的功能远不止占位（见上文的 NumPy、Pydantic、类型注解）。

### 误区 3：`...` 是 Python 3 特有的

❌ `Ellipsis` 从 Python 2 就存在（Python 2.3+），但 `...` 作为字面量是在 Python 3 中引入的。

---

## 5. 实战示例

### NumPy 切片实战

```python
import numpy as np

# 创建 4D 数据 (batch, height, width, channel)
images = np.random.rand(32, 224, 224, 3)

# 取第一个 batch，所有图像的所有通道
first_batch = images[0, ...]  # (224, 224, 3)

# 取所有 batch，所有图像，红色通道
red_channel = images[..., 0]  # (32, 224, 224)

# 取所有 batch，前 100 行，所有列，所有通道
crop = images[:, :100, ...]  # (32, 100, 224, 3)
```

### 类型注解实战

```python
from typing import Tuple, Callable, Optional

# 可变长元组
def sum_numbers(nums: Tuple[float, ...]) -> float:
    return sum(nums)

# 回调函数
def async_operation(callback: Callable[..., None]) -> None:
    # 可以接受任何参数的回调
    callback()

# 结合 Optional
def process(data: Optional[tuple[str, ...]] = None):
    if data is None:
        print("No data provided")
    else:
        print(f"Processing {len(data)} items")
```

### Pydantic 实战

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str
    price: float = Field(..., gt=0)  # 必需字段，大于 0
    description: str = "No description"  # 可选，有默认值
    tags: list[str] = Field(default_factory=list)  # 可选，默认为空列表

# 使用
product = Product(name="Laptop", price=999.99)
print(product.tags)  # []
```

---

## 6. 总结

| 用途 | 代码示例 | 核心价值 |
|------|----------|----------|
| **占位符** | `def func(): ...` | 表示“暂未实现” |
| **NumPy 切片** | `arr[0, ...]` | 简化高维数组切片 |
| **类型注解** | `Tuple[int, ...]` | 表示变长元组 |
| **类型注解** | `Callable[..., int]` | 表示任意参数列表 |
| **Pydantic** | `field: str = ...` | 表示字段必需 |

---

**一句话总结**：
> **Python 中的 `...`（Ellipsis）是一个多功能的内置对象。它最常见的用途是作为代码占位符（比 `pass` 更灵活）、NumPy 中表示“所有剩余维度”的切片操作，以及类型注解中表示变长元组（`Tuple[int, ...]`）或任意参数列表（`Callable[..., int]`）。它的核心思想是“省略”，在需要表示“任意数量/任意部分”时非常有用。**

### ref
[]()