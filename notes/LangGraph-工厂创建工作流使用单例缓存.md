# 工作流适合在工厂中延迟加载并且缓存吗？  

```py
@lru_cache
def create_ingest_workflow():
    # infra / services
    pdf_parser = get_pdf_parser()
    llm_service = get_llm_service()
    object_store = get_object_store()
    embedder = get_embedder()
    item_name_vector_db = get_item_name_vector_db()
    chunks_vector_db = get_chunks_vector_db()

    # nodes
    node_entry = NodeEntry()
    node_pdf_to_md = NodePDFToMD(pdf_parser)
    node_md_img = NodeMDImg(llm_service, object_store)
    node_document_split = NodeDocumentSplit()
    node_item_name_recognition = NodeItemNameRecognition(llm_service, embedder, item_name_vector_db)
    node_bge_embedding = NodeBGEEmbedding(embedder)
    node_import_milvus = NodeImportMilvus(chunks_vector_db)

    return KBImportWorkflow(
        node_entry=node_entry,
        node_pdf_to_md=node_pdf_to_md,
        node_md_img=node_md_img,
        node_document_split=node_document_split,
        node_item_name_recognition=node_item_name_recognition,
        node_bge_embedding=node_bge_embedding,
        node_import_milvus=node_import_milvus
```

**非常适合！** 这恰恰是生产环境中处理“构建成本高、无状态、线程安全”的工作流对象的**最佳实践**。

下面我从“为什么适合”、“需要注意什么”、“有什么替代方案”三个角度帮你彻底搞清楚。

---

## 一、为什么非常适合？

你的 `create_ingest_workflow()` 具备以下三个特征，让它成为 `@lru_cache` 的理想候选：

| 特征 | 你的代码是否符合 | 说明 |
|------|----------------|------|
| **构建成本高** | ✅ 符合 | 创建了 7 个节点 + 6 个基础设施服务（包括 LLM、Embedder、Vector DB 连接等），涉及网络连接、模型加载，耗时可能达数秒 |
| **无状态** | ✅ 符合 | 每个请求传入不同的 `ImportGraphState`，工作流本身不保存请求级别的状态 |
| **线程安全** | ✅ 符合 | LangGraph 的 `CompiledGraph` 是线程安全的，可以多个请求并发调用同一个实例 |

**结论**：用 `@lru_cache` 后，**第一次请求触发构建（耗时 2-5s），后续所有请求直接复用（耗时 < 1ms）**，性能提升 1000 倍以上。

---

## 二、需要注意的 4 个关键点

### 1. 内存占用：不要缓存过多对象
`lru_cache(maxsize=1)` 只缓存一个实例，内存可控。如果你有多个不同类型的工作流（如 `ImportWorkflow`、`QueryWorkflow`、`DeleteWorkflow`），可以分别用单独的 `@lru_cache` 函数缓存，总共也就几个对象。

### 2. 确保所有依赖也是单例
你调用的 `get_pdf_parser()`、`get_embedder()`、`get_chunks_vector_db()` 等，**也应该使用 `@lru_cache` 缓存**，否则每次构建工作流时，这些依赖还是会重新创建，抵消了缓存的优势。

```python
@lru_cache(maxsize=1)
def get_embedder():
    return BGEM3EmbeddingFunction(...)  # 假设这个很重

@lru_cache(maxsize=1)
def get_chunks_vector_db():
    return MilvusChunksVectorDB(...)    # 需要网络连接
```

### 3. 工作流内部节点必须是线程安全的
你的节点（`NodePDFToMD`、`NodeBGEEmbedding` 等）在 `process` 方法中**不能修改自身状态**（如 `self.xxx = ...`），否则多线程并发时会出现数据竞争。

```python
# ❌ 错误：节点内部保存状态
class NodePDFToMD:
    def process(self, state):
        self.last_processed_file = state["file_path"]  # 线程不安全！
        return state

# ✅ 正确：节点无状态，只处理传入的 state
class NodePDFToMD:
    def process(self, state):
        file_path = state["file_path"]  # 只读
        return {"md_content": parse(file_path)}  # 返回新状态
```

如果你的节点需要状态，可以考虑**每个请求创建一个新的节点实例**（这时就不适合缓存工作流了）。

### 4. 懒加载 vs 预热启动
`@lru_cache` 是**懒加载**：第一个请求进来时才构建，用户会等待 2-5 秒。

**优化方案：服务启动时预热**
```python
# main.py 或 app/__init__.py
@app.on_event("startup")
async def startup_event():
    # 提前构建，让第一个请求不等待
    create_ingest_workflow()
    create_query_workflow()
    logger.info("All workflows pre-warmed")
```

---

## 三、替代方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **`@lru_cache` 函数** | 代码最简洁，自带线程安全 | 无法动态替换依赖（如测试时换 Mock） | 生产环境依赖固定，不需要测试替换 |
| **全局变量（模块级）** | 访问最快 | 难以控制初始化时机，单测困难 | 小型脚本 |
| **依赖注入框架（如 FastAPI Depends）** | 可测试性强，支持替换 | 代码稍显繁琐 | 需要单元测试、多租户的场景 |
| **显式单例类** | 控制力最强 | 样板代码多 | 有复杂初始化逻辑的场景 |

---

## 四、你的代码需要微调的地方

### 问题：`get_xx()` 函数内部是否也用了缓存？

```python
# ❌ 如果 get_embedder() 每次都新建，工作流缓存效果打折
def get_embedder():
    return BGEM3EmbeddingFunction(...)  # 每次调用都新建

# ✅ 加 @lru_cache 让它也变成单例
@lru_cache(maxsize=1)
def get_embedder():
    return BGEM3EmbeddingFunction(...)
```

### 建议：把依赖获取放到 `create_ingest_workflow()` 内部

```python
@lru_cache(maxsize=1)
def create_ingest_workflow():
    # 所有依赖都在这里获取（它们内部也应该是 @lru_cache 缓存的）
    pdf_parser = get_pdf_parser()          # 假设已加 @lru_cache
    llm_service = get_llm_service()        # 假设已加 @lru_cache
    object_store = get_object_store()      # 假设已加 @lru_cache
    embedder = get_embedder()              # 假设已加 @lru_cache
    item_name_vector_db = get_item_name_vector_db()
    chunks_vector_db = get_chunks_vector_db()
    
    # ... 构建节点和工作流
    return KBImportWorkflow(...)
```

---

## 五、最终推荐写法（可直接复制）

```python
from functools import lru_cache
from app.workflows.import_workflow import KBImportWorkflow

# ========== 基础设施服务（单例） ==========
@lru_cache(maxsize=1)
def get_pdf_parser():
    from app.services.pdf_parser import PDFParser
    return PDFParser()

@lru_cache(maxsize=1)
def get_llm_service():
    from app.services.llm_service import LLMService
    return LLMService()

@lru_cache(maxsize=1)
def get_object_store():
    from app.services.object_store import MinIOClient
    return MinIOClient()

@lru_cache(maxsize=1)
def get_embedder():
    from app.services.embedding_service import EmbeddingService
    return EmbeddingService()

@lru_cache(maxsize=1)
def get_item_name_vector_db():
    from app.db.item_name_vector_db import ItemNameVectorDB
    return ItemNameVectorDB()

@lru_cache(maxsize=1)
def get_chunks_vector_db():
    from app.db.chunks_vector_db import ChunksVectorDB
    return ChunksVectorDB()

# ========== 工作流工厂（单例） ==========
@lru_cache(maxsize=1)
def create_ingest_workflow():
    """创建导入工作流（全局单例，懒加载）"""
    from app.nodes import (
        NodeEntry, NodePDFToMD, NodeMDImg, NodeDocumentSplit,
        NodeItemNameRecognition, NodeBGEEmbedding, NodeImportMilvus
    )
    
    # 获取所有依赖（均已被缓存）
    pdf_parser = get_pdf_parser()
    llm_service = get_llm_service()
    object_store = get_object_store()
    embedder = get_embedder()
    item_name_vector_db = get_item_name_vector_db()
    chunks_vector_db = get_chunks_vector_db()
    
    # 构建节点
    node_entry = NodeEntry()
    node_pdf_to_md = NodePDFToMD(pdf_parser)
    node_md_img = NodeMDImg(llm_service, object_store)
    node_document_split = NodeDocumentSplit()
    node_item_name_recognition = NodeItemNameRecognition(
        llm_service, embedder, item_name_vector_db
    )
    node_bge_embedding = NodeBGEEmbedding(embedder)
    node_import_milvus = NodeImportMilvus(chunks_vector_db)
    
    return KBImportWorkflow(
        node_entry=node_entry,
        node_pdf_to_md=node_pdf_to_md,
        node_md_img=node_md_img,
        node_document_split=node_document_split,
        node_item_name_recognition=node_item_name_recognition,
        node_bge_embedding=node_bge_embedding,
        node_import_milvus=node_import_milvus,
    )

# ========== 在 FastAPI 中使用 ==========
@app.post("/ingest")
async def ingest_file(file: UploadFile):
    workflow = create_ingest_workflow()  # 首次调用构建，后续秒返回
    result = workflow.run(state={"file_path": file.filename})
    return result
```

---

## 六、总结

| 问题 | 答案 |
|------|------|
| **适合吗？** | ✅ 非常适合 |
| **为什么？** | 构建成本高、无状态、线程安全 |
| **需要注意什么？** | 依赖也需单例 + 节点线程安全 + 内存可控 |
| **最佳实践？** | `@lru_cache` + 服务启动预热 + 依赖全用 `@lru_cache` |

你的设计思路已经非常接近生产级架构了，再补上依赖层的单例缓存，就是一套完整的**“懒加载 + 全局复用”**方案。



# graph如果是单例的话，状态是独立的吗？

**状态是完全独立的！** 这是一个非常好的问题，也是 LangGraph 设计中非常核心的特性。

---

## 核心结论

> **`graph` 本身是无状态的（Stateless），每次调用 `graph.invoke(state)` 或 `graph.stream(state)` 时，状态由传入的 `state` 参数独立提供。**

---

## 一、为什么 graph 单例但状态独立？

### 1. graph 是"执行蓝图"，不是"状态容器"

你可以把 `graph` 理解为一个**工厂流水线的设计图纸**：

- **图纸（graph）**：定义了"物料从哪进→经过哪些工序→成品从哪出"，是固定的。
- **物料（state）**：每次送入的物料（文档）都不同，彼此独立。

`graph` 本身不存储任何数据，它只是**描述了节点之间的连接关系和执行顺序**。真正的数据都在 `state` 这个字典里流动。

### 2. 每次 `invoke` 都创建独立的执行上下文

当你调用 `graph.invoke(state)` 时：

```python
# 两个请求同时进来，共享同一个 graph 单例
workflow = create_ingest_workflow()  # 单例，只构建一次

# 请求 A
state_a = {"file_path": "doc1.pdf", "content": "..."}
result_a = workflow.graph.invoke(state_a)

# 请求 B（同时执行）
state_b = {"file_path": "doc2.pdf", "content": "..."}
result_b = workflow.graph.invoke(state_b)
```

LangGraph 内部会为每次调用创建一个**独立的执行上下文（ExecutionContext）**，包含：
- 当前节点的位置
- 状态的最新值
- 等待执行的节点队列
- 已访问节点的记录

这些上下文是**线程隔离**的，互不影响。

---

## 二、深入：LangGraph 的状态管理机制

### 1. 状态通过复制传递，而非共享

在 `StateGraph` 中，状态从一个节点传递到下一个节点时，LangGraph 会**浅拷贝**状态字典。这意味着：

```python
# 节点 A 修改了 state
def node_a(state):
    state["processed"] = True  # 修改了当前节点的 state 副本
    return state

# 节点 B 收到的 state 是基于节点 A 返回的 state 的新副本
# 不会污染全局状态
```

每个节点都操作的是**当前执行路径上的状态副本**，不会影响到其他并发请求。

### 2. 节点内部状态 vs Graph 状态

这里要区分两种"状态"：

| 状态类型 | 存储位置 | 是否线程安全 | 是否跨请求共享 |
|---------|---------|-------------|---------------|
| **Graph 状态（`state` 字典）** | 每次 `invoke` 独立创建 | ✅ 安全 | ❌ 不共享 |
| **节点实例状态（`self.xxx`）** | 节点对象内部 | ❌ **不安全** | ✅ **共享**（如果节点是单例） |

**关键风险点**：如果你的节点类在 `process` 方法中修改了 `self.xxx`，那就危险了！

```python
# ❌ 危险！节点实例状态被修改
class NodePDFToMD:
    def process(self, state):
        self.last_file = state["file_path"]  # 被请求 A 写入
        # ... 处理逻辑
        return state

# 如果 NodePDFToMD 是单例，请求 B 会覆盖 self.last_file
# 导致请求 A 后续日志打印的是请求 B 的文件名
```

### 3. 如何验证状态独立性？

你可以做个简单实验：

```python
from functools import lru_cache
import time
import threading

@lru_cache(maxsize=1)
def get_graph():
    from langgraph.graph import StateGraph
    graph = StateGraph(dict)
    graph.add_node("echo", lambda s: {"result": s["input"]})
    graph.set_entry_point("echo")
    graph.set_finish_point("echo")
    return graph.compile()

# 两个线程同时调用
def thread_func(name, value):
    graph = get_graph()
    result = graph.invoke({"input": value})
    print(f"Thread {name}: {result}")

t1 = threading.Thread(target=thread_func, args=("A", "Hello"))
t2 = threading.Thread(target=thread_func, args=("B", "World"))
t1.start(); t2.start()
t1.join(); t2.join()

# 输出（互不干扰）：
# Thread A: {'input': 'Hello', 'result': 'Hello'}
# Thread B: {'input': 'World', 'result': 'World'}
```

---

## 三、什么情况下状态会"不独立"？

### 场景 1：节点内部使用了共享资源

```python
class NodePDFToMD:
    def process(self, state):
        # 假设使用了全局连接池
        connection = get_shared_db_connection()  # 全局单例
        connection.execute("INSERT INTO logs ...")  # 线程安全吗？
```

**解决方案**：确保共享资源（数据库连接池、HTTP 客户端）本身是线程安全的（如连接池内部管理了多个连接）。

### 场景 2：节点使用了类变量

```python
class NodeItemNameRecognition:
    cache = {}  # 类变量，所有实例共享
    
    def process(self, state):
        if state["entity"] in self.cache:
            return self.cache[state["entity"]]  # 读安全
        # ...
        self.cache[state["entity"]] = result  # 写操作需要加锁
```

**解决方案**：如果要用缓存，用线程安全的缓存（如 `lru_cache` 或 `cachetools.TTLCache`）。

### 场景 3：使用 `global` 变量

```python
_counter = 0

class NodeEntry:
    def process(self, state):
        global _counter
        _counter += 1  # 线程不安全！
        state["task_id"] = _counter
        return state
```

**解决方案**：使用 `threading.Lock` 或 `uuid.uuid4()` 生成唯一 ID。

---

## 四、你的架构安全检查清单

| 检查项 | 状态 | 说明 |
|-------|------|------|
| `graph` 本身是否无状态？ | ✅ 安全 | 只包含节点定义和边 |
| 每次 `invoke` 是否独立？ | ✅ 安全 | LangGraph 内部保证 |
| 节点是否在 `process` 中修改 `self.xxx`？ | ⚠️ 检查 | 确保所有节点都是无状态的 |
| 节点是否共享了线程安全的资源？ | ✅ 安全 | 连接池、单例服务都应是线程安全的 |
| 节点是否使用了类变量？ | ⚠️ 检查 | 如需要，加锁或用线程安全缓存 |
| 节点是否使用了 `global` 变量？ | ⚠️ 检查 | 避免使用，或加锁保护 |

---

## 五、总结

| 问题 | 答案 |
|------|------|
| **graph 单例，状态独立吗？** | ✅ **完全独立**，每次 `invoke` 创建独立上下文 |
| **并发调用会互相干扰吗？** | ❌ **不会**，只要节点本身无状态 |
| **节点实例是单例，安全吗？** | ✅ **安全**，只要 `process` 方法不修改 `self` |
| **共享资源（DB、HTTP）安全吗？** | ⚠️ **取决于实现**，确保使用线程安全的客户端 |

**结论**：你的 `@lru_cache` 缓存工作流的设计是安全的。只要确保所有节点的 `process` 方法是**纯函数**（只读 `self`，只修改返回的 `state`），并发请求就不会互相干扰。


## ref 
[https://chat.deepseek.com/share/avlp8mfxmw7imy8p9d]()