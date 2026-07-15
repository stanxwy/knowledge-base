```log
(knowledge-base) PS D:\knowledge-base> python -m app.test.06_split_sections

原有方法结果:
标记1: ````
标记2: ~~~
标记3: ```````
识别标题：# 掌柜智库 - 【导入】文档切片节点
识别标题：## 1. 任务目标
识别标题：### 1.1 涉及模块
识别标题：### 1.2 节点在流程中的位置
识别标题：### 1.3 节点在业务中的意义
识别标题：## 2. 节点业务流程
识别标题：### 2.1 节点作用
识别标题：### 2.2 实现思路
识别标题：### 2.3 步骤分解
识别标题：### 2.4 代码实现
识别标题：#### 2.4.1 单元测试
识别标题：#### 2.4.2 主流程定义
识别标题：##### 流程图
识别标题：##### process
识别标题：##### 步骤 1: 获取输入
识别标题：##### 步骤 2: 标题初切
识别标题：###### **关键语法补充说明**
识别标题：##### 步骤 3: 无标题兜底
识别标题：##### 步骤 4: 精细化
识别标题：###### 代码实现
识别标题：###### 切分超长章节
识别标题：###### **关键语法补充说明**
识别标题：###### 合并过短章节
识别标题：##### 步骤 5: 打印统计
识别标题：##### 步骤 6: 备份
识别标题：##### 步骤 7
识别标题：#### 四级标题
识别标题：### 三级标题
识别标题：## 二级标题
识别标题：# 一级标题
识别标题：## 二级标题
识别标题：# 一级标题
识别标题：## 二级标题
识别标题：### 三级标题
识别标题：### 三级标题
识别标题：### 三级标题
文档粗切（按标题切分）完成，共37个章节，标题数量是36，文本共有701行
[
    {'parent_title': '', 'title': '', 'content': '[TOC]\n', 'file_title': 'test'},
    {'parent_title': '', 'title': '# 掌柜智库 - 【导入】文档切片节点', 'content': '# 掌柜智库 - 【导入】文档切片节点\n\n> 本文档详细介绍知识库导入流程的文档切片节点 \n', 'file_title': 'test'},
    {'parent_title': '# 掌柜智库 - 【导入】文档切片节点', 'title': '## 1. 任务目标', 'content': '## 1. 任务目标\n', 'file_title': 'test'},
    {
        'parent_title': '## 1. 任务目标',
        'title': '### 1.1 涉及模块',
        'content': '### 1.1 涉及模块\n\n```\nprocessor/import_processor/nodes/\n├── node_document_split.py     \t\t# 文档切片节点\n```\n',
        'file_title': 'test'
    },
    {
        'parent_title': '## 1. 任务目标',
        'title': '### 1.2 节点在流程中的位置',
        'content': '### 1.2 节点在流程中的位置\n\n```mermaid\nflowchart LR\n    A[START]\n    B[1.任务分发]\n    C[2.PDF结构化解析]\n    D[3.多模态图片理解]\n    E[4.智能文档切片]\n
F[5.主体识别与标签提取]\n    G[6.混合向量化]\n    H[7.数据持久化]\n    I[END]\n    \n    A-->B\n    B-->|PDF|C\n    B-->|Markdown|D\n    C-->D\n    D-->E\n    E-->F\n    F-->G\n    G-->H\n    H-->I\n    \n
%% 核心样式设置：圆角 + 配色区分\n    style A fill:#e8f4f8,stroke:#4299e1,stroke-width:2px,rx:20,ry:20\n    style E fill:#ffff00,stroke:#4299e1,stroke-width:2px\n    style I
fill:#f0f8fb,stroke:#38b2ac,stroke-width:2px,rx:20,ry:20\n```\n\n\n',
        'file_title': 'test'
    },
    {
        'parent_title': '## 1. 任务目标',
        'title': '### 1.3 节点在业务中的意义',
        'content': '### 1.3 节点在业务中的意义\n\n在 RAG（检索增强生成）系统中，用户上传的文档不能直接丢给 LLM 处理，原因如下：\n\n| 问题             | 说明
|\n| ---------------- | ------------------------------------------------------------ |\n| **Token 限制**   | LLM 的上下文窗口有限，无法一次性处理整篇长文档               |\n| **检索不精确**   |
如果不切分，检索时返回整篇文档，噪声过多，LLM 容易产生幻觉   |\n| **向量化成本高** | 整篇文档做 Embedding，计算和存储成本都很高                   |\n| **语义模糊**     |
嵌入模型对短文本的语义表达更精确，长文本的向量表示会"稀释"关键信息 |\n\n切分的质量直接决定了后续检索和回答的质量：\n\n- **切分太粗**：检索到的内容噪声多，LLM 回答不精确\n- **切分太细**：上下文碎片化，LLM
无法理解完整语义\n- **切分得当**：每个 chunk 语义完整、长度适中，检索精准、回答质量高\n\n本节点采用 **"按标题结构切分 + 超长二次切分 + 过短合并"** 的三层策略，在语义完整性和检索精确度之间取得平衡。\n',
        'file_title': 'test'
    },
    {'parent_title': '# 掌柜智库 - 【导入】文档切片节点', 'title': '## 2. 节点业务流程', 'content': '## 2. 节点业务流程\n', 'file_title': 'test'},
    {
        'parent_title': '## 2. 节点业务流程',
        'title': '### 2.1 节点作用',
        'content': '### 2.1 节点作用\n\n将长文档转化为适合向量检索的微观语义单元（Chunk）。通过智能切分策略，在保持语义完整性的前提下，控制切片长度，最大化检索的召回率和准确率。\n',
        'file_title': 'test'
    },
    {
        'parent_title': '## 2. 节点业务流程',
        'title': '### 2.2 实现思路',
        'content': '### 2.2 实现思路\n\n1.  **结构化优先**：摒弃简单的固定字符数切分，优先依据 Markdown 标题层级（Headers）进行逻辑分块，确保同一知识点的连贯性。\n2.  **递归优化**：对于超长段落，采用“段落 ->
句子”的递归切分策略。先按换行符切，若仍超长则按句号切，确保切片不会在句子中间截断。\n3.  **上下文保留**： 在每个切片中保留 `file_title` 和 `parent_title`（父级标题），为后续的 LLM
回答提供丰富的上下文背景。\n',
        'file_title': 'test'
    },
    {
        'parent_title': '## 2. 节点业务流程',
        'title': '### 2.3 步骤分解',
        'content': '### 2.3 步骤分解\n\n本节点负责将 Markdown 文本切分为适合检索的 Chunk（片段）。采用“先按标题切分，再按长度优化”的策略。\n\n1.  **获取输入 (Step 1)**：从 `state` 中提取 Markdown
内容、文件标题等输入数据。\n2.  **标题初切 (Step 2)**：基于 Markdown 标题语法（#）进行第一轮粗略切分，保留层级结构。\n3.  **无标题兜底 (Step 3)**：处理无标题的纯文本文件，避免丢失内容。\n4.  **精细化处理 (Step
4)**：对过长的 Chunk 进行递归切分（按段落/句子），对过短的 Chunk 进行合并。\n5.  **打印统计 (Step 5)**：输出切分结果的统计信息。\n6.  **备份与更新 (Step 6)**：将切分结果更新到 `state` 并备份到本地 JSON
文件。\n',
        'file_title': 'test'
    },
    {'parent_title': '## 2. 节点业务流程', 'title': '### 2.4 代码实现', 'content': '### 2.4 代码实现\n', 'file_title': 'test'},
    {
        'parent_title': '### 2.4 代码实现',
        'title': '#### 2.4.1 单元测试',
        'content': '#### 2.4.1 单元测试\n\n```python\nif __name__ == "__main__":\n\n    setup_logging()\n\n    md_path = r"D:\\output\\hak180产品安全手册\\hak180产品安全手册_new.md"\n    with open(md_path,
"r", encoding="utf-8") as f:\n        md_content = f.read()\n\n    init_state = {\n        "md_path": md_path,\n        "md_content": md_content,\n        "file_title": "hak180产品安全手册"\n    }\n    #
执行文档切分节点\n    node_document_split = NodeDocumentSplit()\n    result = node_document_split(init_state)\n\n    logging.getLogger().info(json.dumps(result, ensure_ascii=False, indent=4))\n```\n',
        'file_title': 'test'
    },
    {'parent_title': '### 2.4 代码实现', 'title': '#### 2.4.2 主流程定义', 'content': '#### 2.4.2 主流程定义\n', 'file_title': 'test'},
    {'parent_title': '#### 2.4.2 主流程定义', 'title': '##### 流程图', 'content': '##### 流程图\n\n![文档切片流程图](images/文档切片流程图3.png)\n', 'file_title': 'test'},
    {
        'parent_title': '#### 2.4.2 主流程定义',
        'title': '##### process',
        'content': '##### process\n\n定义 `node_document_split` ，串联各个步骤。\n\n```python\n# processor/import_processor/nodes/node_document_split.py\nimport json\nimport logging\nimport re\nfrom pathlib
import Path\nfrom typing import Tuple, List, Dict\n\nfrom langchain_text_splitters import RecursiveCharacterTextSplitter\n\nfrom processor.import_processor.base import BaseNode, setup_logging\nfrom
processor.import_processor.exceptions import StateFieldError\nfrom processor.import_processor.state import ImportGraphState\n\nclass NodeDocumentSplit(BaseNode):\n    """\n    节点: 文档切分
(node_document_split)\n    将长文档切分成小的 Chunks (切片) 以便检索。\n    """\n\n    # 覆盖基类的 name 属性，标识节点名称\n    name: str = "node_document_split"\n\n    def process(self, state:
ImportGraphState) -> ImportGraphState:\n        """\n        节点：文档切分（node_document_split）\n        整体流程：加载输入→按MD标题初切→长切短合→统计输出→结果备份\n
核心目的：将长MD文档切分为长度适中的Chunk，适配大模型上下文窗口和向量检索\n        后续扩展点：可在各步骤间新增Chunk元信息补充、自定义切分规则、向量入库前置处理等\n\n        必要参数：md_content、file_title\n
更新参数：chunks\n\n        :param state: 工作流状态对象\n        :return: 更新后的状态对象\n        """\n\n        # 步骤1：加载并标准化输入数据\n        content, file_title =
self._step_1_get_inputs(state)\n\n        # 步骤2：按MD标题进行初次切分\n        sections, title_count, lines_count = self._step_2_split_by_titles(content, file_title)\n\n        # 步骤3：无标题场景兜底处理\n
sections = self._step_3_handle_no_title(content, sections, title_count, file_title)\n\n        # 步骤4：Chunk精细化处理（长切短合\n        sections = self._step_4_refine_chunks(sections)\n\n        #
步骤5：输出文档切分统计信息\n        self._step_5_print_stats(lines_count, sections)\n\n        # 步骤6：Chunk结果本地JSON备份\n        self._step_6_backup(state, sections)\n\n        # 写入状态字典\n
state["chunks"] = sections\n        return state\n```\n',
        'file_title': 'test'
    },
    {
        'parent_title': '#### 2.4.2 主流程定义',
        'title': '##### 步骤 1: 获取输入',
        'content': '##### 步骤 1: 获取输入\n\n从 State 中提取必要的数据，并进行基础清洗。\n\n```python\n   def _step_1_get_inputs(self, state: ImportGraphState) -> Tuple[str, str]:\n        """\n
【步骤1】获取并预处理输入数据\n        功能：从状态字典中提取MD内容/文件标题/最大长度，做基础标准化\n        :param state: 项目状态字典（ImportGraphState），包含md_content等核心键\n        :return:
标准化后的MD内容/文件标题\n        """\n        # 1、非空校验\n        file_title = state.get("file_title")\n        if not file_title:\n            raise StateFieldError(field_name="file_title",
message="文件标题不能为空", expected_type=str)\n\n        md_content = state.get("md_content")\n        if not md_content:\n            raise StateFieldError(field_name="md_content",
message="文件内容不能为空", expected_type=str)\n\n        # 2、基础标准化：统一换行符\n        md_content = md_content.replace("\\r\\n", "\\n").replace("\\r", "\\n")\n\n        return md_content,
file_title\n```\n\n**为什么要统一换行符？**\n\n不同操作系统的换行符不同：\n\n| 操作系统             | 换行符 | 说明        |\n| -------------------- | ------ | ----------- |\n| Windows              | `\\r\\n`
| 回车 + 换行 |\n| Unix/Linux/Mac（新） | `\\n`   | 换行        |\n| Mac（旧版）          | `\\r`   | 回车        |\n\n如果不统一，后续 `md_content.split("\\n")` 按行切分时会出现问题：\n\n- Windows 的 `\\r\\n`
会导致每行末尾残留 `\\r`\n- 旧版 Mac 的 `\\r` 根本不会被 `\\n` 切开，整篇文档变成一行\n',
        'file_title': 'test'
    },
    {
        'parent_title': '#### 2.4.2 主流程定义',
        'title': '##### 步骤 2: 标题初切',
        'content': '##### 步骤 2: 标题初切\n\n基于 Markdown 的标题语法（#）进行第一轮粗略切分。\n\nv1： 代码快只识别 三个返引号 和 三个 波浪线\n\n```python\n    def _step_2_split_by_titles(self, content: str,
file_title: str) -> Tuple[List[Dict[str, str]], int, int]:\n        """\n        【步骤2】按Markdown标题初次切分（核心：按#分级切分，跳过代码块内标题）\n
LangChain前置预处理：将整份MD按标题拆分为独立章节，为后续精细化切分做基础\n        :param content: 标准化后的MD完整内容（字符串）\n        :param file_title: 所属文件标题，用于标记章节归属\n        :return:
切分后的章节列表/有效标题数量/原始文本总行数\n        """\n\n        # 1、定义标题正则\n        # 正则匹配Markdown 1-6级标题（核心规则，适配缩进/标准格式）\n        #
^\\s*：行首允许0/多个空格/Tab（兼容缩进的标题）\n        # #{1,6}：匹配1-6个#（对应MD1-6级标题）\n        # \\s+：#后必须有至少1个空格（区分#是标题还是普通文本）\n        #
.+：标题文字至少1个字符（避免空标题）\n        title_pattern = r\'^\\s*#{1,6}\\s+.+\'\n\n        # 2、初始化需要的数据\n        lines = content.split("\\n")\n        sections = [] #章节列表\n
title_count = 0 #标题数量\n        current_title = "" #当前章节的标题\n        current_lines = [] #当前标题和下一个标题之间的文本内容\n        in_code_block = False
#代码块标记：False当前没在代码块中，True当前在代码块中\n\n        # 3、定义内部函数组装sections列表\n        def _flush_section():\n            """内部辅助函数：将当前缓存的章节写入sections，空缓存则跳过"""\n
if not current_lines:\n                return\n            sections.append({\n                "title": current_title,\n                # 每段使用 \\n换行区分\n                "content":
"\\n".join(current_lines),\n                "file_title": file_title,\n            })\n\n        # 4、逐行遍历，识别标题和普通行以及代码快\n        for line in lines:\n            stripped_line =
line.strip()\n\n            # 4.1 识别代码快边界 ``` 或 ~~~\n            if stripped_line.startswith("```") or stripped_line.startswith("~~~"):\n                in_code_block = not in_code_block\n
current_lines.append(line)\n                continue\n\n            # 4.2 识别标题\n            is_valid_title = (not in_code_block) and re.match(title_pattern, line)\n            if is_valid_title:\n
#遇到标题现将上一个片段写入sesions，再初始化新的章节\n                _flush_section()\n                current_title = stripped_line\n                current_lines = [current_title]\n
title_count += 1\n                self.logger.info(f"识别标题：{current_title}")\n            else:\n                #普通行\n                current_lines.append(line)\n\n        _flush_section()\n
self.logger.info(f"文档粗切（按标题切分）完成，共{len(sections)}个章节，标题数量是{title_count}，文本共有{len(lines)}行")\n        return sections, title_count, len(lines)\n```\n\nv2：
代码快的情况更复杂，多个返引号和多个波浪线，有嵌套的情况\n\n```python\n    def _step_2_split_by_titles(self, content: str, file_title: str) -> Tuple[List[Dict[str, str]], int, int]:\n        """\n
【步骤2】按Markdown标题初次切分（核心：按#分级切分，跳过代码块内标题）\n        LangChain前置预处理：将整份MD按标题拆分为独立章节，为后续精细化切分做基础\n        :param content:
标准化后的MD完整内容（字符串）\n        :param file_title: 所属文件标题，用于标记章节归属\n        :return: 切分后的章节列表/有效标题数量/原始文本总行数\n        """\n\n        # 1、定义标题正则\n        #
正则匹配Markdown 1-6级标题（核心规则，适配缩进/标准格式）\n        # ^\\s*：行首允许0/多个空格/Tab（兼容缩进的标题）\n        # #{1,6}：匹配1-6个#（对应MD1-6级标题）\n        #
\\s+：#后必须有至少1个空格（区分#是标题还是普通文本）\n        # .+：标题文字至少1个字符（避免空标题）\n        title_pattern = r\'^\\s*#{1,6}\\s+.+\'\n\n        # 2、初始化需要的数据\n        lines =
content.split("\\n")\n        sections = [] #章节列表\n        title_count = 0 #标题数量\n        current_title = "" #当前章节的标题\n        current_lines = [] #当前标题和下一个标题之间的文本内容\n
in_code_block = False #代码块标记：False当前没在代码块中，True当前在代码块中\n\n        # 3、定义内部函数组装sections列表\n        def _flush_section():\n
"""内部辅助函数：将当前缓存的章节写入sections，空缓存则跳过"""\n            if not current_lines:\n                return\n            sections.append({\n                "title": current_title,\n
# 每段时间使用 \\n换行区分\n                "content": "\\n".join(current_lines),\n                "file_title": file_title,\n            })\n\n        # 4、逐行遍历，识别标题和普通行以及代码快\n        for
line in lines:\n            striped_line = line.strip()\n            # 4.1 识别代码块边界 ```、~~~、````、~~~~ 等（至少 3 个连续字符）\n            # 使用正则匹配：行首到行尾只有 ` 或 ~ 字符，且数量>=3\n
code_block_marker_match = re.match(r\'^(`{3,}|~{3,})$\', striped_line)\n            if code_block_marker_match:\n                marker = code_block_marker_match.group(1)\n\n                if not
in_code_block:\n                    # 进入代码块，记录开始的标记特征\n                    in_code_block = True\n                    code_block_start_marker = marker\n                elif in_code_block and
striped_line == code_block_start_marker:\n                    # 遇到匹配的结束标记（相同字符且相同长度）\n                    in_code_block = False\n                    code_block_start_marker = None\n\n
current_lines.append(line)\n                continue\n\n            # 4.2 识别标题\n            is_valid_title = (not in_code_block) and re.match(title_pattern, line)\n            if is_valid_title:\n
#遇到标题现将上一个片段写入sesions，再初始化新的章节\n                _flush_section()\n                current_title = stripped_line\n                current_lines = [current_title]\n
title_count += 1\n                self.logger.info(f"识别标题：{current_title}")\n            else:\n                #普通行\n                current_lines.append(line)\n\n        _flush_section()\n
self.logger.info(f"文档粗切（按标题切分）完成，共{len(sections)}个章节，标题数量是{title_count}，文本共有{len(lines)}行")\n        return sections, title_count, len(lines)\n```\n',
        'file_title': 'test'
    },
    {
        'parent_title': '##### 步骤 2: 标题初切',
        'title': '###### **关键语法补充说明**',
        'content': '###### **关键语法补充说明**\n\n正则中的分组标识 圆括号()\n\n```python\nimport re\n\nstripped_line = "````123~~~abc```````"\n\n# 方法2: 保持原有的 match
方式，但更清晰\ncode_block_marker_match = re.match(r\'^(`{3,}|~{3,}).*?(`{3,}|~{3,}).*?(`{3,}|~{3,})$\', stripped_line)\nif code_block_marker_match:\n    marker1 = code_block_marker_match.group(1)\n    marker2
= code_block_marker_match.group(2)\n    marker3 = code_block_marker_match.group(3)\n    print("\\n原有方法结果:")\n    print(f"标记1: {marker1}")\n    print(f"标记2: {marker2}")\n    print(f"标记3:
{marker3}")\n```\n',
        'file_title': 'test'
    },
    {
        'parent_title': '#### 2.4.2 主流程定义',
        'title': '##### 步骤 3: 无标题兜底',
        'content': '##### 步骤 3: 无标题兜底\n\n处理那些没有任何 Markdown 标题的纯文本文件。\n\n```python\n    def _step_3_handle_no_title(self, content: str, sections: List[Dict[str, str]], title_count: int,
file_title: str) -> List[Dict[str, str]]:\n        """\n        【步骤3】无标题兜底处理\n        功能：若MD中未识别到任何标题，将全文作为一个整体处理，避免后续逻辑异常\n        :param content:
标准化后的MD完整内容\n        :param sections: 步骤2切分后的章节列表\n        :param title_count: 步骤2识别的有效标题数量\n        :param file_title: 所属文件标题\n        :return: 兜底后的章节列表\n
"""\n        if title_count == 0:\n            # 无标题情况：替换为单章节，标题为"无标题"\n            self.logger.warning(f"步骤3：未识别到任何MD标题，将全文作为单个章节处理，文件：{file_title}")\n
return [{"title": "无标题", "content": content, "file_title": file_title}]\n        # 有标题情况：直接返回步骤2的结果\n        self.logger.debug(f"步骤3：检测到{title_count}个有效标题，无需兜底处理")\n
return sections\n```\n',
        'file_title': 'test'
    },
    {'parent_title': '#### 2.4.2 主流程定义', 'title': '##### 步骤 4: 精细化', 'content': '##### 步骤 4: 精细化\n', 'file_title': 'test'},
    {
        'parent_title': '##### 步骤 4: 精细化',
        'title': '###### 代码实现',
        'content': '###### 代码实现\n\n调用辅助函数，对过长或过短的 Chunk 进行二次处理。\n\n```python\n    def _step_4_refine_chunks(self, sections: List[Dict[str, str]]) -> List[Dict[str, str]]:\n
"""\n        【步骤4】Chunk精细化处理（核心：长切短合，适配大模型/检索）\n        执行流程：1.切分超长章节 2.合并过短章节 3.父标题兜底（适配Milvus向量库schema）\n        :param sections:
步骤3处理后的章节列表\n        :return: 长度适中、低碎片化的最终Chunk列表\n        """\n\n        # 阶段1：切分超长章节 → 所有章节长度控制在最大长度内\n        refined_split = []\n        for sec in
sections:\n            # 对每个章节执行超长切分，结果平铺加入列表（避免嵌套）\n            refined_split.extend(self._split_long_section(sec))\n
self.logger.info(f"步骤4-1：超长章节切分完成，共生成{len(refined_split)}个初始子Chunk")\n\n        # 阶段2：合并过短章节 → 减少碎片化，提升后续检索/大模型调用效果\n        final_sections =
self._merge_short_sections(refined_split)\n        self.logger.info(f"步骤4-2：过短章节合并完成，最终得到{len(final_sections)}个Chunk")\n\n        # 阶段3：父标题兜底 →
适配Milvus向量库schema（parent_title为必填字段）\n        # 兜底规则：无parent_title则用自身title，title也无则填空字符串\n        for sec in final_sections:\n            if not sec.get("parent_title"):\n
sec["parent_title"] = sec.get("title") or ""\n        self.logger.debug(f"步骤4-3：父标题兜底完成，所有Chunk均包含parent_title字段")\n\n        return final_sections\n```\n',
        'file_title': 'test'
    },
    {
        'parent_title': '##### 步骤 4: 精细化',
        'title': '###### 切分超长章节',
        'content': '###### 切分超长章节\n\n```python\n\n    def _split_long_section(self, section: Dict[str, str]) -> List[Dict[str, str]]:\n        """\n
【辅助函数】超长章节二次切分（核心适配LangChain分割器）\n        功能：单个章节内容超限时，按「段落→句子→空格」从粗到细切分，保留语义\n        切分规则：1.先按空行(段落) 2.再按换行 3.最后按中英文标点/空格\n
:param section: 原始章节字典，必须包含content键，可选title/file_title等\n        :return: 切分后的子章节列表，每个子章节带父标题/序号等元信息\n        """\n        # 内容空值兜底：无内容直接返回原章节\n
content = section.get("content", "")\n        # 长度未超限，无需切分，直接返回原章节（列表格式保持统一）\n        if len(content) <= self.config.max_content_length:\n            return [section]\n\n        #
提取章节标题，用于组装子Chunk前缀（保留标题上下文）\n        title = section.get("title", "")\n        # 标题前缀：带空行分隔，与正文区分开\n        prefix = f"{title}\\n\\n" if title else ""\n        #
计算正文可用长度：总长度 - 标题前缀长度（避免标题占满Chunk额度）\n        available_len = self.config.max_content_length - len(prefix)\n        # 极端情况：标题长度超过阈值，无法切分，返回原章节\n        if
available_len <= 0:\n            self.logger.warning(f"章节标题过长，无法切分：{title[:20]}...")\n            return [section]\n\n        # 清理正文重复标题：避免原章节中正文开头重复标题，导致子Chunk内容冗余\n
body = content\n        if title and body.lstrip().startswith(title):\n            body = body[body.find(title) + len(title):].lstrip()\n\n        #
初始化LangChain递归分割器（核心工具：按优先级分隔符切分，保留语义）\n        # separators：分割符优先级（从粗到细），优先按大语义单元切分，最后才硬拆\n        splitter = RecursiveCharacterTextSplitter(\n
chunk_size=available_len,  # 正文部分最大长度（已扣除标题）\n            chunk_overlap=0,           # 无重叠：按标题切分后语义完整，无需重叠\n            #
分割符优先级：空行(段落)→换行→中文标点→英文标点→空格，最后硬拆（在 chunk_size 位置强制切断）\n            # 先用第一个分隔符进行切分，切分后如果某个 Chunk 还是超过
chunk_size，则继续用下一个优先级的分隔符切分\n            separators=["\\n\\n", "\\n", "。", "！", "？", "；", ".", "!", "?", ";", " "],\n        )\n\n        # 切分正文并组装子章节（带完整元信息，便于溯源）\n
sub_sections = []\n\n        # 遍历切分后的每个文本块，idx 从 1 开始计数\n        for idx, chunk in enumerate(splitter.split_text(body), start=1):\n\n            # 清理空内容：跳过切分后的空字符串\n
text = chunk.strip()\n            if not text:\n                continue\n\n            # 组装子Chunk完整内容 = 标题前缀 + 切分后的正文\n            full_text = (prefix + text).strip()\n\n            #
子章节元信息：保留父级关联，添加序号，便于后续检索/溯源\n            sub_sections.append({\n                "title": f"{title}-{idx}" if title else f"chunk-{idx}",  # 子Chunk标题（带序号）\n
"content": full_text,                                     # 切分后的完整内容\n                "parent_title": title,                                    # 父章节标题（用于后续合并）\n                "part":
idx,                                              # 子Chunk序号\n                "file_title": section.get("file_title"),                  # 所属文件标题\n            })\n\n
self.logger.debug(f"超长章节切分完成：{title} → 生成{len(sub_sections)}个子Chunk")\n        return sub_sections\n\n```\n',
        'file_title': 'test'
    },
    {
        'parent_title': '##### 步骤 4: 精细化',
        'title': '###### **关键语法补充说明**',
        'content': '###### **关键语法补充说明**\n\n1、RecursiveCharacterTextSplitter\n\n这是 LangChain 库提供的一个递归字符文本分割器，它会按照指定的分隔符优先级列表，递归地将文本切分成合适大小的片段。\n\n先用
separators 中的第一个分隔符进行切分，切分后如果某个 Chunk 还是超过 chunk_size，则继续用下一个优先级的分隔符切分。\n\n如果所有分隔符都使用了，还是有某个 Chunk 超过 chunk_size （比如一个超长单词），则会在
chunk_size 位置强制切断\n\n2、enumerate\n\n```python\nenumerate(可迭代对象, start=起始值)\n```\n\nenumerate() 用于同时获取索引和对应的元素值，它会返回一个枚举对象，每次迭代产生一个 (索引，元素)
的元组。\n\n```python\n# 不使用 enumerate\nchunks = splitter.split_text(body)\nfor i in range(len(chunks)):\n idx = i + 1  # 手动计算序号\n chunk = chunks[i]\n # 处理逻辑...\n\n# 使用 enumerate\nfor idx, chunk
in enumerate(splitter.split_text(body), start=1):\n # 直接使用 idx 和 chunk\n # 处理逻辑...\n```\n',
        'file_title': 'test'
    },
    {
        'parent_title': '##### 步骤 4: 精细化',
        'title': '###### 合并过短章节',
        'content': '###### 合并过短章节\n\n```python\n    def _merge_short_sections(self, sections: List[Dict[str, str]]) -> List[Dict[str, str]]:\n        """\n
【辅助函数】过短章节合并（减少碎片化，提升检索效果）\n        核心规则：仅合并「同父标题」且「当前块长度不足阈值」的相邻Chunk，避免跨章节合并\n        :param sections:
待合并的Chunk列表（通常是_split_long_section切分后的结果）\n        :return: 合并后的Chunk列表，长度适中，保留元信息\n        """\n        # 边界处理：空列表直接返回，避免后续索引报错\n        if not
sections:\n            self.logger.debug("待合并Chunk列表为空，直接返回")\n            return []\n\n        merged_sections = []  # 最终合并结果\n        current_chunk = None  #
迭代累加器：保存当前待合并的Chunk\n\n        for sec in sections:\n            # 初始化：第一个Chunk直接作为当前待合并块\n            if current_chunk is None:\n                current_chunk = sec\n
continue\n\n            # 合并条件：1.当前块长度不足阈值 2.与下一块同父标题（同属一个原章节）\n            is_current_short = len(current_chunk["content"]) < self.config.min_content_length\n
is_same_parent = current_chunk.get("parent_title") == sec.get("parent_title")\n\n            if is_current_short and is_same_parent:\n                # 合并前清理：去掉下一块开头重复的父标题，避免内容冗余\n
parent_title = sec.get("parent_title", "")\n                next_content = sec["content"]\n                if parent_title and next_content.startswith(parent_title):\n                    next_content =
next_content[len(parent_title):].lstrip()\n                # 合并内容：空行分隔，保证格式整洁\n                current_chunk["content"] += "\\n\\n" + next_content\n                #
更新子Chunk序号：保留最新序号，便于溯源\n                if "part" in sec:\n                    current_chunk["part"] = sec["part"]\n
self.logger.debug(f"合并短Chunk：{current_chunk.get(\'parent_title\')} → 累计长度{len(current_chunk[\'content\'])}")\n            else:\n                # 不满足合并条件：将当前块加入结果，切换为新的待合并块\n
merged_sections.append(current_chunk)\n                current_chunk = sec\n\n        # 循环结束后，将最后一个待合并块加入结果\n        if current_chunk is not None:\n
merged_sections.append(current_chunk)\n\n        self.logger.debug(f"短Chunk合并完成：原{len(sections)}个 → 合并后{len(merged_sections)}个")\n        return merged_sections\n```\n',
        'file_title': 'test'
    },
    {
        'parent_title': '#### 2.4.2 主流程定义',
        'title': '##### 步骤 5: 打印统计',
        'content': '##### 步骤 5: 打印统计\n\n在控制台输出切分结果的简要统计。\n\n```python\n    def _step_5_print_stats(self, lines_count: int, sections: List[Dict[str, str]]) -> None:\n        """\n
【步骤5】输出文档切分统计信息（日志记录，便于监控/调试）\n        :param lines_count: MD原始文本总行数\n        :param sections: 最终处理后的Chunk列表\n        """\n        chunk_num = len(sections)\n        #
输出核心统计信息：原始行数/最终Chunk数/首个Chunk预览\n        self.logger.info("-" * 50 + " 文档切分统计信息 " + "-" * 50)\n        self.logger.info(f"MD原始文本总行数：{lines_count}")\n
self.logger.info(f"最终生成Chunk数量：{chunk_num}")\n```\n',
        'file_title': 'test'
    },
    {
        'parent_title': '#### 2.4.2 主流程定义',
        'title': '##### 步骤 6: 备份',
        'content': '##### 步骤 6: 备份\n\n将结果备份到本地。\n\n```python\n    def _step_6_backup(self, state: ImportGraphState, sections: List[Dict[str, str]]) -> None:\n        """\n
【步骤6】Chunk结果本地JSON备份（便于调试/问题排查，保留处理结果）\n        :param state: 项目状态字典，需包含md_dir（备份目录）\n        :param sections: 最终处理后的Chunk列表\n        """\n\n        try:\n
# 拼接备份文件路径：固定文件名，便于查找\n            backup_path = "D:/doc" / state.get("file_title") / "chunks.json"\n            # 写入JSON文件：保留中文/格式化缩进，便于人工查看\n            with
open(backup_path, "w", encoding="utf-8") as f:\n                """\n                sections是Python 嵌套数据结构（List[Dict[str, str]]，列表里装字典，字典里可能嵌套字符串 / 数字等），而普通文件写入\n
（如f.write(sections)）仅支持写入字符串，直接写 Python 数据结构会报错。\n                json.dump的核心作用就是：将 Python 原生数据结构（列表、字典、字符串、数字等）直接序列化并写入 JSON
文件，无需手动转换为字符串，\n                同时保证数据格式规范、可跨语言 / 跨场景读取，完美适配「Chunk 列表备份」的需求。\n                """\n                json.dump(\n                    sections,\n
f,\n                    #开启 True："title": "\\u4e00\\u7ea7\\u6807\\u9898"（乱码，无法直接看）；\n                    #开启 False："title": "一级标题"（正常中文，人工可直接阅读）。\n
ensure_ascii=False,  # 保留中文，不转义为\\u编码\n                    indent=2             # 格式化缩进，便于阅读\n                )\n
self.logger.info(f"步骤6：Chunk结果备份成功，备份文件路径：{backup_path}")\n        except Exception as e:\n            # 备份失败仅记录日志，不终止主流程\n
self.logger.error(f"步骤6：Chunk结果备份失败，错误信息：{str(e)}", exc_info=False)\n```',
        'file_title': 'test'
    },
    {'parent_title': '#### 2.4.2 主流程定义', 'title': '##### 步骤 7', 'content': '##### 步骤 7\n内容\n', 'file_title': 'test'},
    {'parent_title': '### 2.4 代码实现', 'title': '#### 四级标题', 'content': '#### 四级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '## 2. 节点业务流程', 'title': '### 三级标题', 'content': '### 三级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '# 掌柜智库 - 【导入】文档切片节点', 'title': '## 二级标题', 'content': '## 二级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '', 'title': '# 一级标题', 'content': '# 一级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '# 一级标题', 'title': '## 二级标题', 'content': '## 二级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '', 'title': '# 一级标题', 'content': '# 一级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '# 一级标题', 'title': '## 二级标题', 'content': '## 二级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '## 二级标题', 'title': '### 三级标题', 'content': '### 三级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '## 二级标题', 'title': '### 三级标题', 'content': '### 三级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '## 二级标题', 'title': '### 三级标题', 'content': '### 三级标题\n内容', 'file_title': 'test'}
]
超长章节切分完成：##### 步骤 2: 标题初切 → 生成3个子Chunk
超长章节切分完成：###### 切分超长章节 → 生成2个子Chunk
超长章节切分完成：###### 合并过短章节 → 生成2个子Chunk
refined
[
    {'parent_title': '', 'title': '', 'content': '[TOC]\n', 'file_title': 'test'},
    {'parent_title': '', 'title': '# 掌柜智库 - 【导入】文档切片节点', 'content': '# 掌柜智库 - 【导入】文档切片节点\n\n> 本文档详细介绍知识库导入流程的文档切片节点 \n', 'file_title': 'test'},
    {'parent_title': '# 掌柜智库 - 【导入】文档切片节点', 'title': '## 1. 任务目标', 'content': '## 1. 任务目标\n', 'file_title': 'test'},
    {
        'parent_title': '## 1. 任务目标',
        'title': '### 1.1 涉及模块',
        'content': '### 1.1 涉及模块\n\n```\nprocessor/import_processor/nodes/\n├── node_document_split.py     \t\t# 文档切片节点\n```\n',
        'file_title': 'test'
    },
    {
        'parent_title': '## 1. 任务目标',
        'title': '### 1.2 节点在流程中的位置',
        'content': '### 1.2 节点在流程中的位置\n\n```mermaid\nflowchart LR\n    A[START]\n    B[1.任务分发]\n    C[2.PDF结构化解析]\n    D[3.多模态图片理解]\n    E[4.智能文档切片]\n
F[5.主体识别与标签提取]\n    G[6.混合向量化]\n    H[7.数据持久化]\n    I[END]\n    \n    A-->B\n    B-->|PDF|C\n    B-->|Markdown|D\n    C-->D\n    D-->E\n    E-->F\n    F-->G\n    G-->H\n    H-->I\n    \n
%% 核心样式设置：圆角 + 配色区分\n    style A fill:#e8f4f8,stroke:#4299e1,stroke-width:2px,rx:20,ry:20\n    style E fill:#ffff00,stroke:#4299e1,stroke-width:2px\n    style I
fill:#f0f8fb,stroke:#38b2ac,stroke-width:2px,rx:20,ry:20\n```\n\n\n',
        'file_title': 'test'
    },
    {
        'parent_title': '## 1. 任务目标',
        'title': '### 1.3 节点在业务中的意义',
        'content': '### 1.3 节点在业务中的意义\n\n在 RAG（检索增强生成）系统中，用户上传的文档不能直接丢给 LLM 处理，原因如下：\n\n| 问题             | 说明
|\n| ---------------- | ------------------------------------------------------------ |\n| **Token 限制**   | LLM 的上下文窗口有限，无法一次性处理整篇长文档               |\n| **检索不精确**   |
如果不切分，检索时返回整篇文档，噪声过多，LLM 容易产生幻觉   |\n| **向量化成本高** | 整篇文档做 Embedding，计算和存储成本都很高                   |\n| **语义模糊**     |
嵌入模型对短文本的语义表达更精确，长文本的向量表示会"稀释"关键信息 |\n\n切分的质量直接决定了后续检索和回答的质量：\n\n- **切分太粗**：检索到的内容噪声多，LLM 回答不精确\n- **切分太细**：上下文碎片化，LLM
无法理解完整语义\n- **切分得当**：每个 chunk 语义完整、长度适中，检索精准、回答质量高\n\n本节点采用 **"按标题结构切分 + 超长二次切分 + 过短合并"** 的三层策略，在语义完整性和检索精确度之间取得平衡。\n',
        'file_title': 'test'
    },
    {'parent_title': '# 掌柜智库 - 【导入】文档切片节点', 'title': '## 2. 节点业务流程', 'content': '## 2. 节点业务流程\n', 'file_title': 'test'},
    {
        'parent_title': '## 2. 节点业务流程',
        'title': '### 2.1 节点作用',
        'content': '### 2.1 节点作用\n\n将长文档转化为适合向量检索的微观语义单元（Chunk）。通过智能切分策略，在保持语义完整性的前提下，控制切片长度，最大化检索的召回率和准确率。\n',
        'file_title': 'test'
    },
    {
        'parent_title': '## 2. 节点业务流程',
        'title': '### 2.2 实现思路',
        'content': '### 2.2 实现思路\n\n1.  **结构化优先**：摒弃简单的固定字符数切分，优先依据 Markdown 标题层级（Headers）进行逻辑分块，确保同一知识点的连贯性。\n2.  **递归优化**：对于超长段落，采用“段落 ->
句子”的递归切分策略。先按换行符切，若仍超长则按句号切，确保切片不会在句子中间截断。\n3.  **上下文保留**： 在每个切片中保留 `file_title` 和 `parent_title`（父级标题），为后续的 LLM
回答提供丰富的上下文背景。\n',
        'file_title': 'test'
    },
    {
        'parent_title': '## 2. 节点业务流程',
        'title': '### 2.3 步骤分解',
        'content': '### 2.3 步骤分解\n\n本节点负责将 Markdown 文本切分为适合检索的 Chunk（片段）。采用“先按标题切分，再按长度优化”的策略。\n\n1.  **获取输入 (Step 1)**：从 `state` 中提取 Markdown
内容、文件标题等输入数据。\n2.  **标题初切 (Step 2)**：基于 Markdown 标题语法（#）进行第一轮粗略切分，保留层级结构。\n3.  **无标题兜底 (Step 3)**：处理无标题的纯文本文件，避免丢失内容。\n4.  **精细化处理 (Step
4)**：对过长的 Chunk 进行递归切分（按段落/句子），对过短的 Chunk 进行合并。\n5.  **打印统计 (Step 5)**：输出切分结果的统计信息。\n6.  **备份与更新 (Step 6)**：将切分结果更新到 `state` 并备份到本地 JSON
文件。\n',
        'file_title': 'test'
    },
    {'parent_title': '## 2. 节点业务流程', 'title': '### 2.4 代码实现', 'content': '### 2.4 代码实现\n', 'file_title': 'test'},
    {
        'parent_title': '### 2.4 代码实现',
        'title': '#### 2.4.1 单元测试',
        'content': '#### 2.4.1 单元测试\n\n```python\nif __name__ == "__main__":\n\n    setup_logging()\n\n    md_path = r"D:\\output\\hak180产品安全手册\\hak180产品安全手册_new.md"\n    with open(md_path,
"r", encoding="utf-8") as f:\n        md_content = f.read()\n\n    init_state = {\n        "md_path": md_path,\n        "md_content": md_content,\n        "file_title": "hak180产品安全手册"\n    }\n    #
执行文档切分节点\n    node_document_split = NodeDocumentSplit()\n    result = node_document_split(init_state)\n\n    logging.getLogger().info(json.dumps(result, ensure_ascii=False, indent=4))\n```\n',
        'file_title': 'test'
    },
    {'parent_title': '### 2.4 代码实现', 'title': '#### 2.4.2 主流程定义', 'content': '#### 2.4.2 主流程定义\n', 'file_title': 'test'},
    {'parent_title': '#### 2.4.2 主流程定义', 'title': '##### 流程图', 'content': '##### 流程图\n\n![文档切片流程图](images/文档切片流程图3.png)\n', 'file_title': 'test'},
    {
        'parent_title': '#### 2.4.2 主流程定义',
        'title': '##### process',
        'content': '##### process\n\n定义 `node_document_split` ，串联各个步骤。\n\n```python\n# processor/import_processor/nodes/node_document_split.py\nimport json\nimport logging\nimport re\nfrom pathlib
import Path\nfrom typing import Tuple, List, Dict\n\nfrom langchain_text_splitters import RecursiveCharacterTextSplitter\n\nfrom processor.import_processor.base import BaseNode, setup_logging\nfrom
processor.import_processor.exceptions import StateFieldError\nfrom processor.import_processor.state import ImportGraphState\n\nclass NodeDocumentSplit(BaseNode):\n    """\n    节点: 文档切分
(node_document_split)\n    将长文档切分成小的 Chunks (切片) 以便检索。\n    """\n\n    # 覆盖基类的 name 属性，标识节点名称\n    name: str = "node_document_split"\n\n    def process(self, state:
ImportGraphState) -> ImportGraphState:\n        """\n        节点：文档切分（node_document_split）\n        整体流程：加载输入→按MD标题初切→长切短合→统计输出→结果备份\n
核心目的：将长MD文档切分为长度适中的Chunk，适配大模型上下文窗口和向量检索\n        后续扩展点：可在各步骤间新增Chunk元信息补充、自定义切分规则、向量入库前置处理等\n\n        必要参数：md_content、file_title\n
更新参数：chunks\n\n        :param state: 工作流状态对象\n        :return: 更新后的状态对象\n        """\n\n        # 步骤1：加载并标准化输入数据\n        content, file_title =
self._step_1_get_inputs(state)\n\n        # 步骤2：按MD标题进行初次切分\n        sections, title_count, lines_count = self._step_2_split_by_titles(content, file_title)\n\n        # 步骤3：无标题场景兜底处理\n
sections = self._step_3_handle_no_title(content, sections, title_count, file_title)\n\n        # 步骤4：Chunk精细化处理（长切短合\n        sections = self._step_4_refine_chunks(sections)\n\n        #
步骤5：输出文档切分统计信息\n        self._step_5_print_stats(lines_count, sections)\n\n        # 步骤6：Chunk结果本地JSON备份\n        self._step_6_backup(state, sections)\n\n        # 写入状态字典\n
state["chunks"] = sections\n        return state\n```\n',
        'file_title': 'test'
    },
    {
        'parent_title': '#### 2.4.2 主流程定义',
        'title': '##### 步骤 1: 获取输入',
        'content': '##### 步骤 1: 获取输入\n\n从 State 中提取必要的数据，并进行基础清洗。\n\n```python\n   def _step_1_get_inputs(self, state: ImportGraphState) -> Tuple[str, str]:\n        """\n
【步骤1】获取并预处理输入数据\n        功能：从状态字典中提取MD内容/文件标题/最大长度，做基础标准化\n        :param state: 项目状态字典（ImportGraphState），包含md_content等核心键\n        :return:
标准化后的MD内容/文件标题\n        """\n        # 1、非空校验\n        file_title = state.get("file_title")\n        if not file_title:\n            raise StateFieldError(field_name="file_title",
message="文件标题不能为空", expected_type=str)\n\n        md_content = state.get("md_content")\n        if not md_content:\n            raise StateFieldError(field_name="md_content",
message="文件内容不能为空", expected_type=str)\n\n        # 2、基础标准化：统一换行符\n        md_content = md_content.replace("\\r\\n", "\\n").replace("\\r", "\\n")\n\n        return md_content,
file_title\n```\n\n**为什么要统一换行符？**\n\n不同操作系统的换行符不同：\n\n| 操作系统             | 换行符 | 说明        |\n| -------------------- | ------ | ----------- |\n| Windows              | `\\r\\n`
| 回车 + 换行 |\n| Unix/Linux/Mac（新） | `\\n`   | 换行        |\n| Mac（旧版）          | `\\r`   | 回车        |\n\n如果不统一，后续 `md_content.split("\\n")` 按行切分时会出现问题：\n\n- Windows 的 `\\r\\n`
会导致每行末尾残留 `\\r`\n- 旧版 Mac 的 `\\r` 根本不会被 `\\n` 切开，整篇文档变成一行\n',
        'file_title': 'test'
    },
    {
        'title': '##### 步骤 2: 标题初切-1',
        'content': '##### 步骤 2: 标题初切\n\n基于 Markdown 的标题语法（#）进行第一轮粗略切分。\n\nv1： 代码快只识别 三个返引号 和 三个 波浪线\n\n```python\n    def _step_2_split_by_titles(self, content: str,
file_title: str) -> Tuple[List[Dict[str, str]], int, int]:\n        """\n        【步骤2】按Markdown标题初次切分（核心：按#分级切分，跳过代码块内标题）\n
LangChain前置预处理：将整份MD按标题拆分为独立章节，为后续精细化切分做基础\n        :param content: 标准化后的MD完整内容（字符串）\n        :param file_title: 所属文件标题，用于标记章节归属\n        :return:
切分后的章节列表/有效标题数量/原始文本总行数\n        """\n\n        # 1、定义标题正则\n        # 正则匹配Markdown 1-6级标题（核心规则，适配缩进/标准格式）\n        #
^\\s*：行首允许0/多个空格/Tab（兼容缩进的标题）\n        # #{1,6}：匹配1-6个#（对应MD1-6级标题）\n        # \\s+：#后必须有至少1个空格（区分#是标题还是普通文本）\n        #
.+：标题文字至少1个字符（避免空标题）\n        title_pattern = r\'^\\s*#{1,6}\\s+.+\'\n\n        # 2、初始化需要的数据\n        lines = content.split("\\n")\n        sections = [] #章节列表\n
title_count = 0 #标题数量\n        current_title = "" #当前章节的标题\n        current_lines = [] #当前标题和下一个标题之间的文本内容\n        in_code_block = False
#代码块标记：False当前没在代码块中，True当前在代码块中\n\n        # 3、定义内部函数组装sections列表\n        def _flush_section():\n            """内部辅助函数：将当前缓存的章节写入sections，空缓存则跳过"""\n
if not current_lines:\n                return\n            sections.append({\n                "title": current_title,\n                # 每段使用 \\n换行区分\n                "content":
"\\n".join(current_lines),\n                "file_title": file_title,\n            })\n\n        # 4、逐行遍历，识别标题和普通行以及代码快\n        for line in lines:\n            stripped_line =
line.strip()\n\n            # 4.1 识别代码快边界 ``` 或 ~~~\n            if stripped_line.startswith("```") or stripped_line.startswith("~~~"):\n                in_code_block = not in_code_block\n
current_lines.append(line)\n                continue',
        'parent_title': '##### 步骤 2: 标题初切',
        'part': 1,
        'file_title': 'test'
    },
    {
        'title': '##### 步骤 2: 标题初切-2',
        'content': '##### 步骤 2: 标题初切\n\n# 4.2 识别标题\n            is_valid_title = (not in_code_block) and re.match(title_pattern, line)\n            if is_valid_title:\n
#遇到标题现将上一个片段写入sesions，再初始化新的章节\n                _flush_section()\n                current_title = stripped_line\n                current_lines = [current_title]\n
title_count += 1\n                self.logger.info(f"识别标题：{current_title}")\n            else:\n                #普通行\n                current_lines.append(line)\n\n        _flush_section()\n
self.logger.info(f"文档粗切（按标题切分）完成，共{len(sections)}个章节，标题数量是{title_count}，文本共有{len(lines)}行")\n        return sections, title_count, len(lines)\n```\n\nv2：
代码快的情况更复杂，多个返引号和多个波浪线，有嵌套的情况\n\n```python\n    def _step_2_split_by_titles(self, content: str, file_title: str) -> Tuple[List[Dict[str, str]], int, int]:\n        """\n
【步骤2】按Markdown标题初次切分（核心：按#分级切分，跳过代码块内标题）\n        LangChain前置预处理：将整份MD按标题拆分为独立章节，为后续精细化切分做基础\n        :param content:
标准化后的MD完整内容（字符串）\n        :param file_title: 所属文件标题，用于标记章节归属\n        :return: 切分后的章节列表/有效标题数量/原始文本总行数\n        """\n\n        # 1、定义标题正则\n        #
正则匹配Markdown 1-6级标题（核心规则，适配缩进/标准格式）\n        # ^\\s*：行首允许0/多个空格/Tab（兼容缩进的标题）\n        # #{1,6}：匹配1-6个#（对应MD1-6级标题）\n        #
\\s+：#后必须有至少1个空格（区分#是标题还是普通文本）\n        # .+：标题文字至少1个字符（避免空标题）\n        title_pattern = r\'^\\s*#{1,6}\\s+.+\'\n\n        # 2、初始化需要的数据\n        lines =
content.split("\\n")\n        sections = [] #章节列表\n        title_count = 0 #标题数量\n        current_title = "" #当前章节的标题\n        current_lines = [] #当前标题和下一个标题之间的文本内容\n
in_code_block = False #代码块标记：False当前没在代码块中，True当前在代码块中\n\n        # 3、定义内部函数组装sections列表\n        def _flush_section():\n
"""内部辅助函数：将当前缓存的章节写入sections，空缓存则跳过"""\n            if not current_lines:\n                return\n            sections.append({\n                "title": current_title,\n
# 每段时间使用 \\n换行区分\n                "content": "\\n".join(current_lines),\n                "file_title": file_title,\n            })',
        'parent_title': '##### 步骤 2: 标题初切',
        'part': 2,
        'file_title': 'test'
    },
    {
        'title': '##### 步骤 2: 标题初切-3',
        'content': '##### 步骤 2: 标题初切\n\n# 4、逐行遍历，识别标题和普通行以及代码快\n        for line in lines:\n            striped_line = line.strip()\n            # 4.1 识别代码块边界
```、~~~、````、~~~~ 等（至少 3 个连续字符）\n            # 使用正则匹配：行首到行尾只有 ` 或 ~ 字符，且数量>=3\n            code_block_marker_match = re.match(r\'^(`{3,}|~{3,})$\', striped_line)\n
if code_block_marker_match:\n                marker = code_block_marker_match.group(1)\n\n                if not in_code_block:\n                    # 进入代码块，记录开始的标记特征\n
in_code_block = True\n                    code_block_start_marker = marker\n                elif in_code_block and striped_line == code_block_start_marker:\n                    #
遇到匹配的结束标记（相同字符且相同长度）\n                    in_code_block = False\n                    code_block_start_marker = None\n\n                current_lines.append(line)\n
continue\n\n            # 4.2 识别标题\n            is_valid_title = (not in_code_block) and re.match(title_pattern, line)\n            if is_valid_title:\n
#遇到标题现将上一个片段写入sesions，再初始化新的章节\n                _flush_section()\n                current_title = stripped_line\n                current_lines = [current_title]\n
title_count += 1\n                self.logger.info(f"识别标题：{current_title}")\n            else:\n                #普通行\n                current_lines.append(line)\n\n        _flush_section()\n
self.logger.info(f"文档粗切（按标题切分）完成，共{len(sections)}个章节，标题数量是{title_count}，文本共有{len(lines)}行")\n        return sections, title_count, len(lines)\n```',
        'parent_title': '##### 步骤 2: 标题初切',
        'part': 3,
        'file_title': 'test'
    },
    {
        'parent_title': '##### 步骤 2: 标题初切',
        'title': '###### **关键语法补充说明**',
        'content': '###### **关键语法补充说明**\n\n正则中的分组标识 圆括号()\n\n```python\nimport re\n\nstripped_line = "````123~~~abc```````"\n\n# 方法2: 保持原有的 match
方式，但更清晰\ncode_block_marker_match = re.match(r\'^(`{3,}|~{3,}).*?(`{3,}|~{3,}).*?(`{3,}|~{3,})$\', stripped_line)\nif code_block_marker_match:\n    marker1 = code_block_marker_match.group(1)\n    marker2
= code_block_marker_match.group(2)\n    marker3 = code_block_marker_match.group(3)\n    print("\\n原有方法结果:")\n    print(f"标记1: {marker1}")\n    print(f"标记2: {marker2}")\n    print(f"标记3:
{marker3}")\n```\n',
        'file_title': 'test'
    },
    {
        'parent_title': '#### 2.4.2 主流程定义',
        'title': '##### 步骤 3: 无标题兜底',
        'content': '##### 步骤 3: 无标题兜底\n\n处理那些没有任何 Markdown 标题的纯文本文件。\n\n```python\n    def _step_3_handle_no_title(self, content: str, sections: List[Dict[str, str]], title_count: int,
file_title: str) -> List[Dict[str, str]]:\n        """\n        【步骤3】无标题兜底处理\n        功能：若MD中未识别到任何标题，将全文作为一个整体处理，避免后续逻辑异常\n        :param content:
标准化后的MD完整内容\n        :param sections: 步骤2切分后的章节列表\n        :param title_count: 步骤2识别的有效标题数量\n        :param file_title: 所属文件标题\n        :return: 兜底后的章节列表\n
"""\n        if title_count == 0:\n            # 无标题情况：替换为单章节，标题为"无标题"\n            self.logger.warning(f"步骤3：未识别到任何MD标题，将全文作为单个章节处理，文件：{file_title}")\n
return [{"title": "无标题", "content": content, "file_title": file_title}]\n        # 有标题情况：直接返回步骤2的结果\n        self.logger.debug(f"步骤3：检测到{title_count}个有效标题，无需兜底处理")\n
return sections\n```\n',
        'file_title': 'test'
    },
    {'parent_title': '#### 2.4.2 主流程定义', 'title': '##### 步骤 4: 精细化', 'content': '##### 步骤 4: 精细化\n', 'file_title': 'test'},
    {
        'parent_title': '##### 步骤 4: 精细化',
        'title': '###### 代码实现',
        'content': '###### 代码实现\n\n调用辅助函数，对过长或过短的 Chunk 进行二次处理。\n\n```python\n    def _step_4_refine_chunks(self, sections: List[Dict[str, str]]) -> List[Dict[str, str]]:\n
"""\n        【步骤4】Chunk精细化处理（核心：长切短合，适配大模型/检索）\n        执行流程：1.切分超长章节 2.合并过短章节 3.父标题兜底（适配Milvus向量库schema）\n        :param sections:
步骤3处理后的章节列表\n        :return: 长度适中、低碎片化的最终Chunk列表\n        """\n\n        # 阶段1：切分超长章节 → 所有章节长度控制在最大长度内\n        refined_split = []\n        for sec in
sections:\n            # 对每个章节执行超长切分，结果平铺加入列表（避免嵌套）\n            refined_split.extend(self._split_long_section(sec))\n
self.logger.info(f"步骤4-1：超长章节切分完成，共生成{len(refined_split)}个初始子Chunk")\n\n        # 阶段2：合并过短章节 → 减少碎片化，提升后续检索/大模型调用效果\n        final_sections =
self._merge_short_sections(refined_split)\n        self.logger.info(f"步骤4-2：过短章节合并完成，最终得到{len(final_sections)}个Chunk")\n\n        # 阶段3：父标题兜底 →
适配Milvus向量库schema（parent_title为必填字段）\n        # 兜底规则：无parent_title则用自身title，title也无则填空字符串\n        for sec in final_sections:\n            if not sec.get("parent_title"):\n
sec["parent_title"] = sec.get("title") or ""\n        self.logger.debug(f"步骤4-3：父标题兜底完成，所有Chunk均包含parent_title字段")\n\n        return final_sections\n```\n',
        'file_title': 'test'
    },
    {
        'title': '###### 切分超长章节-1',
        'content': '###### 切分超长章节\n\n```python\n\n    def _split_long_section(self, section: Dict[str, str]) -> List[Dict[str, str]]:\n        """\n
【辅助函数】超长章节二次切分（核心适配LangChain分割器）\n        功能：单个章节内容超限时，按「段落→句子→空格」从粗到细切分，保留语义\n        切分规则：1.先按空行(段落) 2.再按换行 3.最后按中英文标点/空格\n
:param section: 原始章节字典，必须包含content键，可选title/file_title等\n        :return: 切分后的子章节列表，每个子章节带父标题/序号等元信息\n        """\n        # 内容空值兜底：无内容直接返回原章节\n
content = section.get("content", "")\n        # 长度未超限，无需切分，直接返回原章节（列表格式保持统一）\n        if len(content) <= self.config.max_content_length:\n            return [section]\n\n        #
提取章节标题，用于组装子Chunk前缀（保留标题上下文）\n        title = section.get("title", "")\n        # 标题前缀：带空行分隔，与正文区分开\n        prefix = f"{title}\\n\\n" if title else ""\n        #
计算正文可用长度：总长度 - 标题前缀长度（避免标题占满Chunk额度）\n        available_len = self.config.max_content_length - len(prefix)\n        # 极端情况：标题长度超过阈值，无法切分，返回原章节\n        if
available_len <= 0:\n            self.logger.warning(f"章节标题过长，无法切分：{title[:20]}...")\n            return [section]\n\n        # 清理正文重复标题：避免原章节中正文开头重复标题，导致子Chunk内容冗余\n
body = content\n        if title and body.lstrip().startswith(title):\n            body = body[body.find(title) + len(title):].lstrip()\n\n        #
初始化LangChain递归分割器（核心工具：按优先级分隔符切分，保留语义）\n        # separators：分割符优先级（从粗到细），优先按大语义单元切分，最后才硬拆\n        splitter = RecursiveCharacterTextSplitter(\n
chunk_size=available_len,  # 正文部分最大长度（已扣除标题）\n            chunk_overlap=0,           # 无重叠：按标题切分后语义完整，无需重叠\n            #
分割符优先级：空行(段落)→换行→中文标点→英文标点→空格，最后硬拆（在 chunk_size 位置强制切断）\n            # 先用第一个分隔符进行切分，切分后如果某个 Chunk 还是超过
chunk_size，则继续用下一个优先级的分隔符切分\n            separators=["\\n\\n", "\\n", "。", "！", "？", "；", ".", "!", "?", ";", " "],\n        )\n\n        # 切分正文并组装子章节（带完整元信息，便于溯源）\n
sub_sections = []\n\n        # 遍历切分后的每个文本块，idx 从 1 开始计数\n        for idx, chunk in enumerate(splitter.split_text(body), start=1):\n\n            # 清理空内容：跳过切分后的空字符串\n
text = chunk.strip()\n            if not text:\n                continue',
        'parent_title': '###### 切分超长章节',
        'part': 1,
        'file_title': 'test'
    },
    {
        'title': '###### 切分超长章节-2',
        'content': '###### 切分超长章节\n\n# 组装子Chunk完整内容 = 标题前缀 + 切分后的正文\n            full_text = (prefix + text).strip()\n\n            #
子章节元信息：保留父级关联，添加序号，便于后续检索/溯源\n            sub_sections.append({\n                "title": f"{title}-{idx}" if title else f"chunk-{idx}",  # 子Chunk标题（带序号）\n
"content": full_text,                                     # 切分后的完整内容\n                "parent_title": title,                                    # 父章节标题（用于后续合并）\n                "part":
idx,                                              # 子Chunk序号\n                "file_title": section.get("file_title"),                  # 所属文件标题\n            })\n\n
self.logger.debug(f"超长章节切分完成：{title} → 生成{len(sub_sections)}个子Chunk")\n        return sub_sections\n\n```',
        'parent_title': '###### 切分超长章节',
        'part': 2,
        'file_title': 'test'
    },
    {
        'parent_title': '##### 步骤 4: 精细化',
        'title': '###### **关键语法补充说明**',
        'content': '###### **关键语法补充说明**\n\n1、RecursiveCharacterTextSplitter\n\n这是 LangChain 库提供的一个递归字符文本分割器，它会按照指定的分隔符优先级列表，递归地将文本切分成合适大小的片段。\n\n先用
separators 中的第一个分隔符进行切分，切分后如果某个 Chunk 还是超过 chunk_size，则继续用下一个优先级的分隔符切分。\n\n如果所有分隔符都使用了，还是有某个 Chunk 超过 chunk_size （比如一个超长单词），则会在
chunk_size 位置强制切断\n\n2、enumerate\n\n```python\nenumerate(可迭代对象, start=起始值)\n```\n\nenumerate() 用于同时获取索引和对应的元素值，它会返回一个枚举对象，每次迭代产生一个 (索引，元素)
的元组。\n\n```python\n# 不使用 enumerate\nchunks = splitter.split_text(body)\nfor i in range(len(chunks)):\n idx = i + 1  # 手动计算序号\n chunk = chunks[i]\n # 处理逻辑...\n\n# 使用 enumerate\nfor idx, chunk
in enumerate(splitter.split_text(body), start=1):\n # 直接使用 idx 和 chunk\n # 处理逻辑...\n```\n',
        'file_title': 'test'
    },
    {
        'title': '###### 合并过短章节-1',
        'content': '###### 合并过短章节\n\n```python\n    def _merge_short_sections(self, sections: List[Dict[str, str]]) -> List[Dict[str, str]]:\n        """\n
【辅助函数】过短章节合并（减少碎片化，提升检索效果）\n        核心规则：仅合并「同父标题」且「当前块长度不足阈值」的相邻Chunk，避免跨章节合并\n        :param sections:
待合并的Chunk列表（通常是_split_long_section切分后的结果）\n        :return: 合并后的Chunk列表，长度适中，保留元信息\n        """\n        # 边界处理：空列表直接返回，避免后续索引报错\n        if not
sections:\n            self.logger.debug("待合并Chunk列表为空，直接返回")\n            return []\n\n        merged_sections = []  # 最终合并结果\n        current_chunk = None  #
迭代累加器：保存当前待合并的Chunk\n\n        for sec in sections:\n            # 初始化：第一个Chunk直接作为当前待合并块\n            if current_chunk is None:\n                current_chunk = sec\n
continue\n\n            # 合并条件：1.当前块长度不足阈值 2.与下一块同父标题（同属一个原章节）\n            is_current_short = len(current_chunk["content"]) < self.config.min_content_length\n
is_same_parent = current_chunk.get("parent_title") == sec.get("parent_title")\n\n            if is_current_short and is_same_parent:\n                # 合并前清理：去掉下一块开头重复的父标题，避免内容冗余\n
parent_title = sec.get("parent_title", "")\n                next_content = sec["content"]\n                if parent_title and next_content.startswith(parent_title):\n                    next_content =
next_content[len(parent_title):].lstrip()\n                # 合并内容：空行分隔，保证格式整洁\n                current_chunk["content"] += "\\n\\n" + next_content\n                #
更新子Chunk序号：保留最新序号，便于溯源\n                if "part" in sec:\n                    current_chunk["part"] = sec["part"]\n
self.logger.debug(f"合并短Chunk：{current_chunk.get(\'parent_title\')} → 累计长度{len(current_chunk[\'content\'])}")\n            else:\n                # 不满足合并条件：将当前块加入结果，切换为新的待合并块\n
merged_sections.append(current_chunk)\n                current_chunk = sec\n\n        # 循环结束后，将最后一个待合并块加入结果\n        if current_chunk is not None:\n
merged_sections.append(current_chunk)',
        'parent_title': '###### 合并过短章节',
        'part': 1,
        'file_title': 'test'
    },
    {
        'title': '###### 合并过短章节-2',
        'content': '###### 合并过短章节\n\nself.logger.debug(f"短Chunk合并完成：原{len(sections)}个 → 合并后{len(merged_sections)}个")\n        return merged_sections\n```',
        'parent_title': '###### 合并过短章节',
        'part': 2,
        'file_title': 'test'
    },
    {
        'parent_title': '#### 2.4.2 主流程定义',
        'title': '##### 步骤 5: 打印统计',
        'content': '##### 步骤 5: 打印统计\n\n在控制台输出切分结果的简要统计。\n\n```python\n    def _step_5_print_stats(self, lines_count: int, sections: List[Dict[str, str]]) -> None:\n        """\n
【步骤5】输出文档切分统计信息（日志记录，便于监控/调试）\n        :param lines_count: MD原始文本总行数\n        :param sections: 最终处理后的Chunk列表\n        """\n        chunk_num = len(sections)\n        #
输出核心统计信息：原始行数/最终Chunk数/首个Chunk预览\n        self.logger.info("-" * 50 + " 文档切分统计信息 " + "-" * 50)\n        self.logger.info(f"MD原始文本总行数：{lines_count}")\n
self.logger.info(f"最终生成Chunk数量：{chunk_num}")\n```\n',
        'file_title': 'test'
    },
    {
        'parent_title': '#### 2.4.2 主流程定义',
        'title': '##### 步骤 6: 备份',
        'content': '##### 步骤 6: 备份\n\n将结果备份到本地。\n\n```python\n    def _step_6_backup(self, state: ImportGraphState, sections: List[Dict[str, str]]) -> None:\n        """\n
【步骤6】Chunk结果本地JSON备份（便于调试/问题排查，保留处理结果）\n        :param state: 项目状态字典，需包含md_dir（备份目录）\n        :param sections: 最终处理后的Chunk列表\n        """\n\n        try:\n
# 拼接备份文件路径：固定文件名，便于查找\n            backup_path = "D:/doc" / state.get("file_title") / "chunks.json"\n            # 写入JSON文件：保留中文/格式化缩进，便于人工查看\n            with
open(backup_path, "w", encoding="utf-8") as f:\n                """\n                sections是Python 嵌套数据结构（List[Dict[str, str]]，列表里装字典，字典里可能嵌套字符串 / 数字等），而普通文件写入\n
（如f.write(sections)）仅支持写入字符串，直接写 Python 数据结构会报错。\n                json.dump的核心作用就是：将 Python 原生数据结构（列表、字典、字符串、数字等）直接序列化并写入 JSON
文件，无需手动转换为字符串，\n                同时保证数据格式规范、可跨语言 / 跨场景读取，完美适配「Chunk 列表备份」的需求。\n                """\n                json.dump(\n                    sections,\n
f,\n                    #开启 True："title": "\\u4e00\\u7ea7\\u6807\\u9898"（乱码，无法直接看）；\n                    #开启 False："title": "一级标题"（正常中文，人工可直接阅读）。\n
ensure_ascii=False,  # 保留中文，不转义为\\u编码\n                    indent=2             # 格式化缩进，便于阅读\n                )\n
self.logger.info(f"步骤6：Chunk结果备份成功，备份文件路径：{backup_path}")\n        except Exception as e:\n            # 备份失败仅记录日志，不终止主流程\n
self.logger.error(f"步骤6：Chunk结果备份失败，错误信息：{str(e)}", exc_info=False)\n```',
        'file_title': 'test'
    },
    {'parent_title': '#### 2.4.2 主流程定义', 'title': '##### 步骤 7', 'content': '##### 步骤 7\n内容\n', 'file_title': 'test'},
    {'parent_title': '### 2.4 代码实现', 'title': '#### 四级标题', 'content': '#### 四级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '## 2. 节点业务流程', 'title': '### 三级标题', 'content': '### 三级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '# 掌柜智库 - 【导入】文档切片节点', 'title': '## 二级标题', 'content': '## 二级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '', 'title': '# 一级标题', 'content': '# 一级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '# 一级标题', 'title': '## 二级标题', 'content': '## 二级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '', 'title': '# 一级标题', 'content': '# 一级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '# 一级标题', 'title': '## 二级标题', 'content': '## 二级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '## 二级标题', 'title': '### 三级标题', 'content': '### 三级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '## 二级标题', 'title': '### 三级标题', 'content': '### 三级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '## 二级标题', 'title': '### 三级标题', 'content': '### 三级标题\n内容', 'file_title': 'test'}
]
  满足合并条件 = True
合并短Chunk： → 累计长度54，合并Chunk 2 个
 # 掌柜智库 - 【导入】文档切片节点 满足合并条件 = False
# 掌柜智库 - 【导入】文档切片节点 ## 1. 任务目标 满足合并条件 = False
## 1. 任务目标 ## 1. 任务目标 满足合并条件 = True
合并短Chunk：## 1. 任务目标 → 累计长度621，合并Chunk 2 个
## 1. 任务目标 ## 1. 任务目标 满足合并条件 = True
## 1. 任务目标 # 掌柜智库 - 【导入】文档切片节点 满足合并条件 = False
# 掌柜智库 - 【导入】文档切片节点 ## 2. 节点业务流程 满足合并条件 = False
## 2. 节点业务流程 ## 2. 节点业务流程 满足合并条件 = True
合并短Chunk：## 2. 节点业务流程 → 累计长度331，合并Chunk 2 个
## 2. 节点业务流程 ## 2. 节点业务流程 满足合并条件 = True
合并短Chunk：## 2. 节点业务流程 → 累计长度725，合并Chunk 3 个
## 2. 节点业务流程 ## 2. 节点业务流程 满足合并条件 = True
## 2. 节点业务流程 ### 2.4 代码实现 满足合并条件 = False
### 2.4 代码实现 ### 2.4 代码实现 满足合并条件 = True
### 2.4 代码实现 #### 2.4.2 主流程定义 满足合并条件 = False
#### 2.4.2 主流程定义 #### 2.4.2 主流程定义 满足合并条件 = True
合并短Chunk：#### 2.4.2 主流程定义 → 累计长度1746，合并Chunk 2 个
#### 2.4.2 主流程定义 #### 2.4.2 主流程定义 满足合并条件 = True
#### 2.4.2 主流程定义 ##### 步骤 2: 标题初切 满足合并条件 = False
##### 步骤 2: 标题初切 ##### 步骤 2: 标题初切 满足合并条件 = True
##### 步骤 2: 标题初切 ##### 步骤 2: 标题初切 满足合并条件 = True
##### 步骤 2: 标题初切 ##### 步骤 2: 标题初切 满足合并条件 = True
##### 步骤 2: 标题初切 #### 2.4.2 主流程定义 满足合并条件 = False
#### 2.4.2 主流程定义 #### 2.4.2 主流程定义 满足合并条件 = True
#### 2.4.2 主流程定义 ##### 步骤 4: 精细化 满足合并条件 = False
##### 步骤 4: 精细化 ###### 切分超长章节 满足合并条件 = False
###### 切分超长章节 ###### 切分超长章节 满足合并条件 = True
###### 切分超长章节 ##### 步骤 4: 精细化 满足合并条件 = False
##### 步骤 4: 精细化 ###### 合并过短章节 满足合并条件 = False
###### 合并过短章节 ###### 合并过短章节 满足合并条件 = True
###### 合并过短章节 #### 2.4.2 主流程定义 满足合并条件 = False
#### 2.4.2 主流程定义 #### 2.4.2 主流程定义 满足合并条件 = True
#### 2.4.2 主流程定义 #### 2.4.2 主流程定义 满足合并条件 = True
#### 2.4.2 主流程定义 ### 2.4 代码实现 满足合并条件 = False
### 2.4 代码实现 ## 2. 节点业务流程 满足合并条件 = False
## 2. 节点业务流程 # 掌柜智库 - 【导入】文档切片节点 满足合并条件 = False
# 掌柜智库 - 【导入】文档切片节点  满足合并条件 = False
 # 一级标题 满足合并条件 = False
# 一级标题  满足合并条件 = False
 # 一级标题 满足合并条件 = False
# 一级标题 ## 二级标题 满足合并条件 = False
## 二级标题 ## 二级标题 满足合并条件 = True
合并短Chunk：## 二级标题 → 累计长度26，合并Chunk 2 个
## 二级标题 ## 二级标题 满足合并条件 = True
合并短Chunk：## 二级标题 → 累计长度39，合并Chunk 3 个
短Chunk合并完成：原41个 → 合并后34个
final
[
    {'parent_title': '', 'title': '', 'content': '[TOC]\n\n\n# 掌柜智库 - 【导入】文档切片节点\n\n> 本文档详细介绍知识库导入流程的文档切片节点 \n', 'file_title': 'test'},
    {'parent_title': '# 掌柜智库 - 【导入】文档切片节点', 'title': '## 1. 任务目标', 'content': '## 1. 任务目标\n', 'file_title': 'test'},
    {
        'parent_title': '## 1. 任务目标',
        'title': '### 1.1 涉及模块',
        'content': '### 1.1 涉及模块\n\n```\nprocessor/import_processor/nodes/\n├── node_document_split.py     \t\t# 文档切片节点\n```\n\n\n### 1.2 节点在流程中的位置\n\n```mermaid\nflowchart LR\n
A[START]\n    B[1.任务分发]\n    C[2.PDF结构化解析]\n    D[3.多模态图片理解]\n    E[4.智能文档切片]\n    F[5.主体识别与标签提取]\n    G[6.混合向量化]\n    H[7.数据持久化]\n    I[END]\n    \n    A-->B\n
B-->|PDF|C\n    B-->|Markdown|D\n    C-->D\n    D-->E\n    E-->F\n    F-->G\n    G-->H\n    H-->I\n    \n    %% 核心样式设置：圆角 + 配色区分\n    style A
fill:#e8f4f8,stroke:#4299e1,stroke-width:2px,rx:20,ry:20\n    style E fill:#ffff00,stroke:#4299e1,stroke-width:2px\n    style I fill:#f0f8fb,stroke:#38b2ac,stroke-width:2px,rx:20,ry:20\n```\n\n\n',
        'file_title': 'test'
    },
    {
        'parent_title': '## 1. 任务目标',
        'title': '### 1.3 节点在业务中的意义',
        'content': '### 1.3 节点在业务中的意义\n\n在 RAG（检索增强生成）系统中，用户上传的文档不能直接丢给 LLM 处理，原因如下：\n\n| 问题             | 说明
|\n| ---------------- | ------------------------------------------------------------ |\n| **Token 限制**   | LLM 的上下文窗口有限，无法一次性处理整篇长文档               |\n| **检索不精确**   |
如果不切分，检索时返回整篇文档，噪声过多，LLM 容易产生幻觉   |\n| **向量化成本高** | 整篇文档做 Embedding，计算和存储成本都很高                   |\n| **语义模糊**     |
嵌入模型对短文本的语义表达更精确，长文本的向量表示会"稀释"关键信息 |\n\n切分的质量直接决定了后续检索和回答的质量：\n\n- **切分太粗**：检索到的内容噪声多，LLM 回答不精确\n- **切分太细**：上下文碎片化，LLM
无法理解完整语义\n- **切分得当**：每个 chunk 语义完整、长度适中，检索精准、回答质量高\n\n本节点采用 **"按标题结构切分 + 超长二次切分 + 过短合并"** 的三层策略，在语义完整性和检索精确度之间取得平衡。\n',
        'file_title': 'test'
    },
    {'parent_title': '# 掌柜智库 - 【导入】文档切片节点', 'title': '## 2. 节点业务流程', 'content': '## 2. 节点业务流程\n', 'file_title': 'test'},
    {
        'parent_title': '## 2. 节点业务流程',
        'title': '### 2.1 节点作用',
        'content': '### 2.1 节点作用\n\n将长文档转化为适合向量检索的微观语义单元（Chunk）。通过智能切分策略，在保持语义完整性的前提下，控制切片长度，最大化检索的召回率和准确率。\n\n\n### 2.2 实现思路\n\n1.
**结构化优先**：摒弃简单的固定字符数切分，优先依据 Markdown 标题层级（Headers）进行逻辑分块，确保同一知识点的连贯性。\n2.  **递归优化**：对于超长段落，采用“段落 ->
句子”的递归切分策略。先按换行符切，若仍超长则按句号切，确保切片不会在句子中间截断。\n3.  **上下文保留**： 在每个切片中保留 `file_title` 和 `parent_title`（父级标题），为后续的 LLM
回答提供丰富的上下文背景。\n\n\n### 2.3 步骤分解\n\n本节点负责将 Markdown 文本切分为适合检索的 Chunk（片段）。采用“先按标题切分，再按长度优化”的策略。\n\n1.  **获取输入 (Step 1)**：从 `state` 中提取 Markdown
内容、文件标题等输入数据。\n2.  **标题初切 (Step 2)**：基于 Markdown 标题语法（#）进行第一轮粗略切分，保留层级结构。\n3.  **无标题兜底 (Step 3)**：处理无标题的纯文本文件，避免丢失内容。\n4.  **精细化处理 (Step
4)**：对过长的 Chunk 进行递归切分（按段落/句子），对过短的 Chunk 进行合并。\n5.  **打印统计 (Step 5)**：输出切分结果的统计信息。\n6.  **备份与更新 (Step 6)**：将切分结果更新到 `state` 并备份到本地 JSON
文件。\n',
        'file_title': 'test'
    },
    {'parent_title': '## 2. 节点业务流程', 'title': '### 2.4 代码实现', 'content': '### 2.4 代码实现\n', 'file_title': 'test'},
    {
        'parent_title': '### 2.4 代码实现',
        'title': '#### 2.4.1 单元测试',
        'content': '#### 2.4.1 单元测试\n\n```python\nif __name__ == "__main__":\n\n    setup_logging()\n\n    md_path = r"D:\\output\\hak180产品安全手册\\hak180产品安全手册_new.md"\n    with open(md_path,
"r", encoding="utf-8") as f:\n        md_content = f.read()\n\n    init_state = {\n        "md_path": md_path,\n        "md_content": md_content,\n        "file_title": "hak180产品安全手册"\n    }\n    #
执行文档切分节点\n    node_document_split = NodeDocumentSplit()\n    result = node_document_split(init_state)\n\n    logging.getLogger().info(json.dumps(result, ensure_ascii=False, indent=4))\n```\n',
        'file_title': 'test'
    },
    {'parent_title': '### 2.4 代码实现', 'title': '#### 2.4.2 主流程定义', 'content': '#### 2.4.2 主流程定义\n', 'file_title': 'test'},
    {
        'parent_title': '#### 2.4.2 主流程定义',
        'title': '##### 流程图',
        'content': '##### 流程图\n\n![文档切片流程图](images/文档切片流程图3.png)\n\n\n##### process\n\n定义 `node_document_split` ，串联各个步骤。\n\n```python\n#
processor/import_processor/nodes/node_document_split.py\nimport json\nimport logging\nimport re\nfrom pathlib import Path\nfrom typing import Tuple, List, Dict\n\nfrom langchain_text_splitters import
RecursiveCharacterTextSplitter\n\nfrom processor.import_processor.base import BaseNode, setup_logging\nfrom processor.import_processor.exceptions import StateFieldError\nfrom processor.import_processor.state
import ImportGraphState\n\nclass NodeDocumentSplit(BaseNode):\n    """\n    节点: 文档切分 (node_document_split)\n    将长文档切分成小的 Chunks (切片) 以便检索。\n    """\n\n    # 覆盖基类的 name
属性，标识节点名称\n    name: str = "node_document_split"\n\n    def process(self, state: ImportGraphState) -> ImportGraphState:\n        """\n        节点：文档切分（node_document_split）\n
整体流程：加载输入→按MD标题初切→长切短合→统计输出→结果备份\n        核心目的：将长MD文档切分为长度适中的Chunk，适配大模型上下文窗口和向量检索\n
后续扩展点：可在各步骤间新增Chunk元信息补充、自定义切分规则、向量入库前置处理等\n\n        必要参数：md_content、file_title\n        更新参数：chunks\n\n        :param state: 工作流状态对象\n        :return:
更新后的状态对象\n        """\n\n        # 步骤1：加载并标准化输入数据\n        content, file_title = self._step_1_get_inputs(state)\n\n        # 步骤2：按MD标题进行初次切分\n        sections, title_count,
lines_count = self._step_2_split_by_titles(content, file_title)\n\n        # 步骤3：无标题场景兜底处理\n        sections = self._step_3_handle_no_title(content, sections, title_count, file_title)\n\n        #
步骤4：Chunk精细化处理（长切短合\n        sections = self._step_4_refine_chunks(sections)\n\n        # 步骤5：输出文档切分统计信息\n        self._step_5_print_stats(lines_count, sections)\n\n        #
步骤6：Chunk结果本地JSON备份\n        self._step_6_backup(state, sections)\n\n        # 写入状态字典\n        state["chunks"] = sections\n        return state\n```\n',
        'file_title': 'test'
    },
    {
        'parent_title': '#### 2.4.2 主流程定义',
        'title': '##### 步骤 1: 获取输入',
        'content': '##### 步骤 1: 获取输入\n\n从 State 中提取必要的数据，并进行基础清洗。\n\n```python\n   def _step_1_get_inputs(self, state: ImportGraphState) -> Tuple[str, str]:\n        """\n
【步骤1】获取并预处理输入数据\n        功能：从状态字典中提取MD内容/文件标题/最大长度，做基础标准化\n        :param state: 项目状态字典（ImportGraphState），包含md_content等核心键\n        :return:
标准化后的MD内容/文件标题\n        """\n        # 1、非空校验\n        file_title = state.get("file_title")\n        if not file_title:\n            raise StateFieldError(field_name="file_title",
message="文件标题不能为空", expected_type=str)\n\n        md_content = state.get("md_content")\n        if not md_content:\n            raise StateFieldError(field_name="md_content",
message="文件内容不能为空", expected_type=str)\n\n        # 2、基础标准化：统一换行符\n        md_content = md_content.replace("\\r\\n", "\\n").replace("\\r", "\\n")\n\n        return md_content,
file_title\n```\n\n**为什么要统一换行符？**\n\n不同操作系统的换行符不同：\n\n| 操作系统             | 换行符 | 说明        |\n| -------------------- | ------ | ----------- |\n| Windows              | `\\r\\n`
| 回车 + 换行 |\n| Unix/Linux/Mac（新） | `\\n`   | 换行        |\n| Mac（旧版）          | `\\r`   | 回车        |\n\n如果不统一，后续 `md_content.split("\\n")` 按行切分时会出现问题：\n\n- Windows 的 `\\r\\n`
会导致每行末尾残留 `\\r`\n- 旧版 Mac 的 `\\r` 根本不会被 `\\n` 切开，整篇文档变成一行\n',
        'file_title': 'test'
    },
    {
        'title': '##### 步骤 2: 标题初切-1',
        'content': '##### 步骤 2: 标题初切\n\n基于 Markdown 的标题语法（#）进行第一轮粗略切分。\n\nv1： 代码快只识别 三个返引号 和 三个 波浪线\n\n```python\n    def _step_2_split_by_titles(self, content: str,
file_title: str) -> Tuple[List[Dict[str, str]], int, int]:\n        """\n        【步骤2】按Markdown标题初次切分（核心：按#分级切分，跳过代码块内标题）\n
LangChain前置预处理：将整份MD按标题拆分为独立章节，为后续精细化切分做基础\n        :param content: 标准化后的MD完整内容（字符串）\n        :param file_title: 所属文件标题，用于标记章节归属\n        :return:
切分后的章节列表/有效标题数量/原始文本总行数\n        """\n\n        # 1、定义标题正则\n        # 正则匹配Markdown 1-6级标题（核心规则，适配缩进/标准格式）\n        #
^\\s*：行首允许0/多个空格/Tab（兼容缩进的标题）\n        # #{1,6}：匹配1-6个#（对应MD1-6级标题）\n        # \\s+：#后必须有至少1个空格（区分#是标题还是普通文本）\n        #
.+：标题文字至少1个字符（避免空标题）\n        title_pattern = r\'^\\s*#{1,6}\\s+.+\'\n\n        # 2、初始化需要的数据\n        lines = content.split("\\n")\n        sections = [] #章节列表\n
title_count = 0 #标题数量\n        current_title = "" #当前章节的标题\n        current_lines = [] #当前标题和下一个标题之间的文本内容\n        in_code_block = False
#代码块标记：False当前没在代码块中，True当前在代码块中\n\n        # 3、定义内部函数组装sections列表\n        def _flush_section():\n            """内部辅助函数：将当前缓存的章节写入sections，空缓存则跳过"""\n
if not current_lines:\n                return\n            sections.append({\n                "title": current_title,\n                # 每段使用 \\n换行区分\n                "content":
"\\n".join(current_lines),\n                "file_title": file_title,\n            })\n\n        # 4、逐行遍历，识别标题和普通行以及代码快\n        for line in lines:\n            stripped_line =
line.strip()\n\n            # 4.1 识别代码快边界 ``` 或 ~~~\n            if stripped_line.startswith("```") or stripped_line.startswith("~~~"):\n                in_code_block = not in_code_block\n
current_lines.append(line)\n                continue',
        'parent_title': '##### 步骤 2: 标题初切',
        'part': 1,
        'file_title': 'test'
    },
    {
        'title': '##### 步骤 2: 标题初切-2',
        'content': '##### 步骤 2: 标题初切\n\n# 4.2 识别标题\n            is_valid_title = (not in_code_block) and re.match(title_pattern, line)\n            if is_valid_title:\n
#遇到标题现将上一个片段写入sesions，再初始化新的章节\n                _flush_section()\n                current_title = stripped_line\n                current_lines = [current_title]\n
title_count += 1\n                self.logger.info(f"识别标题：{current_title}")\n            else:\n                #普通行\n                current_lines.append(line)\n\n        _flush_section()\n
self.logger.info(f"文档粗切（按标题切分）完成，共{len(sections)}个章节，标题数量是{title_count}，文本共有{len(lines)}行")\n        return sections, title_count, len(lines)\n```\n\nv2：
代码快的情况更复杂，多个返引号和多个波浪线，有嵌套的情况\n\n```python\n    def _step_2_split_by_titles(self, content: str, file_title: str) -> Tuple[List[Dict[str, str]], int, int]:\n        """\n
【步骤2】按Markdown标题初次切分（核心：按#分级切分，跳过代码块内标题）\n        LangChain前置预处理：将整份MD按标题拆分为独立章节，为后续精细化切分做基础\n        :param content:
标准化后的MD完整内容（字符串）\n        :param file_title: 所属文件标题，用于标记章节归属\n        :return: 切分后的章节列表/有效标题数量/原始文本总行数\n        """\n\n        # 1、定义标题正则\n        #
正则匹配Markdown 1-6级标题（核心规则，适配缩进/标准格式）\n        # ^\\s*：行首允许0/多个空格/Tab（兼容缩进的标题）\n        # #{1,6}：匹配1-6个#（对应MD1-6级标题）\n        #
\\s+：#后必须有至少1个空格（区分#是标题还是普通文本）\n        # .+：标题文字至少1个字符（避免空标题）\n        title_pattern = r\'^\\s*#{1,6}\\s+.+\'\n\n        # 2、初始化需要的数据\n        lines =
content.split("\\n")\n        sections = [] #章节列表\n        title_count = 0 #标题数量\n        current_title = "" #当前章节的标题\n        current_lines = [] #当前标题和下一个标题之间的文本内容\n
in_code_block = False #代码块标记：False当前没在代码块中，True当前在代码块中\n\n        # 3、定义内部函数组装sections列表\n        def _flush_section():\n
"""内部辅助函数：将当前缓存的章节写入sections，空缓存则跳过"""\n            if not current_lines:\n                return\n            sections.append({\n                "title": current_title,\n
# 每段时间使用 \\n换行区分\n                "content": "\\n".join(current_lines),\n                "file_title": file_title,\n            })',
        'parent_title': '##### 步骤 2: 标题初切',
        'part': 2,
        'file_title': 'test'
    },
    {
        'title': '##### 步骤 2: 标题初切-3',
        'content': '##### 步骤 2: 标题初切\n\n# 4、逐行遍历，识别标题和普通行以及代码快\n        for line in lines:\n            striped_line = line.strip()\n            # 4.1 识别代码块边界
```、~~~、````、~~~~ 等（至少 3 个连续字符）\n            # 使用正则匹配：行首到行尾只有 ` 或 ~ 字符，且数量>=3\n            code_block_marker_match = re.match(r\'^(`{3,}|~{3,})$\', striped_line)\n
if code_block_marker_match:\n                marker = code_block_marker_match.group(1)\n\n                if not in_code_block:\n                    # 进入代码块，记录开始的标记特征\n
in_code_block = True\n                    code_block_start_marker = marker\n                elif in_code_block and striped_line == code_block_start_marker:\n                    #
遇到匹配的结束标记（相同字符且相同长度）\n                    in_code_block = False\n                    code_block_start_marker = None\n\n                current_lines.append(line)\n
continue\n\n            # 4.2 识别标题\n            is_valid_title = (not in_code_block) and re.match(title_pattern, line)\n            if is_valid_title:\n
#遇到标题现将上一个片段写入sesions，再初始化新的章节\n                _flush_section()\n                current_title = stripped_line\n                current_lines = [current_title]\n
title_count += 1\n                self.logger.info(f"识别标题：{current_title}")\n            else:\n                #普通行\n                current_lines.append(line)\n\n        _flush_section()\n
self.logger.info(f"文档粗切（按标题切分）完成，共{len(sections)}个章节，标题数量是{title_count}，文本共有{len(lines)}行")\n        return sections, title_count, len(lines)\n```',
        'parent_title': '##### 步骤 2: 标题初切',
        'part': 3,
        'file_title': 'test'
    },
    {
        'parent_title': '##### 步骤 2: 标题初切',
        'title': '###### **关键语法补充说明**',
        'content': '###### **关键语法补充说明**\n\n正则中的分组标识 圆括号()\n\n```python\nimport re\n\nstripped_line = "````123~~~abc```````"\n\n# 方法2: 保持原有的 match
方式，但更清晰\ncode_block_marker_match = re.match(r\'^(`{3,}|~{3,}).*?(`{3,}|~{3,}).*?(`{3,}|~{3,})$\', stripped_line)\nif code_block_marker_match:\n    marker1 = code_block_marker_match.group(1)\n    marker2
= code_block_marker_match.group(2)\n    marker3 = code_block_marker_match.group(3)\n    print("\\n原有方法结果:")\n    print(f"标记1: {marker1}")\n    print(f"标记2: {marker2}")\n    print(f"标记3:
{marker3}")\n```\n',
        'file_title': 'test'
    },
    {
        'parent_title': '#### 2.4.2 主流程定义',
        'title': '##### 步骤 3: 无标题兜底',
        'content': '##### 步骤 3: 无标题兜底\n\n处理那些没有任何 Markdown 标题的纯文本文件。\n\n```python\n    def _step_3_handle_no_title(self, content: str, sections: List[Dict[str, str]], title_count: int,
file_title: str) -> List[Dict[str, str]]:\n        """\n        【步骤3】无标题兜底处理\n        功能：若MD中未识别到任何标题，将全文作为一个整体处理，避免后续逻辑异常\n        :param content:
标准化后的MD完整内容\n        :param sections: 步骤2切分后的章节列表\n        :param title_count: 步骤2识别的有效标题数量\n        :param file_title: 所属文件标题\n        :return: 兜底后的章节列表\n
"""\n        if title_count == 0:\n            # 无标题情况：替换为单章节，标题为"无标题"\n            self.logger.warning(f"步骤3：未识别到任何MD标题，将全文作为单个章节处理，文件：{file_title}")\n
return [{"title": "无标题", "content": content, "file_title": file_title}]\n        # 有标题情况：直接返回步骤2的结果\n        self.logger.debug(f"步骤3：检测到{title_count}个有效标题，无需兜底处理")\n
return sections\n```\n',
        'file_title': 'test'
    },
    {'parent_title': '#### 2.4.2 主流程定义', 'title': '##### 步骤 4: 精细化', 'content': '##### 步骤 4: 精细化\n', 'file_title': 'test'},
    {
        'parent_title': '##### 步骤 4: 精细化',
        'title': '###### 代码实现',
        'content': '###### 代码实现\n\n调用辅助函数，对过长或过短的 Chunk 进行二次处理。\n\n```python\n    def _step_4_refine_chunks(self, sections: List[Dict[str, str]]) -> List[Dict[str, str]]:\n
"""\n        【步骤4】Chunk精细化处理（核心：长切短合，适配大模型/检索）\n        执行流程：1.切分超长章节 2.合并过短章节 3.父标题兜底（适配Milvus向量库schema）\n        :param sections:
步骤3处理后的章节列表\n        :return: 长度适中、低碎片化的最终Chunk列表\n        """\n\n        # 阶段1：切分超长章节 → 所有章节长度控制在最大长度内\n        refined_split = []\n        for sec in
sections:\n            # 对每个章节执行超长切分，结果平铺加入列表（避免嵌套）\n            refined_split.extend(self._split_long_section(sec))\n
self.logger.info(f"步骤4-1：超长章节切分完成，共生成{len(refined_split)}个初始子Chunk")\n\n        # 阶段2：合并过短章节 → 减少碎片化，提升后续检索/大模型调用效果\n        final_sections =
self._merge_short_sections(refined_split)\n        self.logger.info(f"步骤4-2：过短章节合并完成，最终得到{len(final_sections)}个Chunk")\n\n        # 阶段3：父标题兜底 →
适配Milvus向量库schema（parent_title为必填字段）\n        # 兜底规则：无parent_title则用自身title，title也无则填空字符串\n        for sec in final_sections:\n            if not sec.get("parent_title"):\n
sec["parent_title"] = sec.get("title") or ""\n        self.logger.debug(f"步骤4-3：父标题兜底完成，所有Chunk均包含parent_title字段")\n\n        return final_sections\n```\n',
        'file_title': 'test'
    },
    {
        'title': '###### 切分超长章节-1',
        'content': '###### 切分超长章节\n\n```python\n\n    def _split_long_section(self, section: Dict[str, str]) -> List[Dict[str, str]]:\n        """\n
【辅助函数】超长章节二次切分（核心适配LangChain分割器）\n        功能：单个章节内容超限时，按「段落→句子→空格」从粗到细切分，保留语义\n        切分规则：1.先按空行(段落) 2.再按换行 3.最后按中英文标点/空格\n
:param section: 原始章节字典，必须包含content键，可选title/file_title等\n        :return: 切分后的子章节列表，每个子章节带父标题/序号等元信息\n        """\n        # 内容空值兜底：无内容直接返回原章节\n
content = section.get("content", "")\n        # 长度未超限，无需切分，直接返回原章节（列表格式保持统一）\n        if len(content) <= self.config.max_content_length:\n            return [section]\n\n        #
提取章节标题，用于组装子Chunk前缀（保留标题上下文）\n        title = section.get("title", "")\n        # 标题前缀：带空行分隔，与正文区分开\n        prefix = f"{title}\\n\\n" if title else ""\n        #
计算正文可用长度：总长度 - 标题前缀长度（避免标题占满Chunk额度）\n        available_len = self.config.max_content_length - len(prefix)\n        # 极端情况：标题长度超过阈值，无法切分，返回原章节\n        if
available_len <= 0:\n            self.logger.warning(f"章节标题过长，无法切分：{title[:20]}...")\n            return [section]\n\n        # 清理正文重复标题：避免原章节中正文开头重复标题，导致子Chunk内容冗余\n
body = content\n        if title and body.lstrip().startswith(title):\n            body = body[body.find(title) + len(title):].lstrip()\n\n        #
初始化LangChain递归分割器（核心工具：按优先级分隔符切分，保留语义）\n        # separators：分割符优先级（从粗到细），优先按大语义单元切分，最后才硬拆\n        splitter = RecursiveCharacterTextSplitter(\n
chunk_size=available_len,  # 正文部分最大长度（已扣除标题）\n            chunk_overlap=0,           # 无重叠：按标题切分后语义完整，无需重叠\n            #
分割符优先级：空行(段落)→换行→中文标点→英文标点→空格，最后硬拆（在 chunk_size 位置强制切断）\n            # 先用第一个分隔符进行切分，切分后如果某个 Chunk 还是超过
chunk_size，则继续用下一个优先级的分隔符切分\n            separators=["\\n\\n", "\\n", "。", "！", "？", "；", ".", "!", "?", ";", " "],\n        )\n\n        # 切分正文并组装子章节（带完整元信息，便于溯源）\n
sub_sections = []\n\n        # 遍历切分后的每个文本块，idx 从 1 开始计数\n        for idx, chunk in enumerate(splitter.split_text(body), start=1):\n\n            # 清理空内容：跳过切分后的空字符串\n
text = chunk.strip()\n            if not text:\n                continue',
        'parent_title': '###### 切分超长章节',
        'part': 1,
        'file_title': 'test'
    },
    {
        'title': '###### 切分超长章节-2',
        'content': '###### 切分超长章节\n\n# 组装子Chunk完整内容 = 标题前缀 + 切分后的正文\n            full_text = (prefix + text).strip()\n\n            #
子章节元信息：保留父级关联，添加序号，便于后续检索/溯源\n            sub_sections.append({\n                "title": f"{title}-{idx}" if title else f"chunk-{idx}",  # 子Chunk标题（带序号）\n
"content": full_text,                                     # 切分后的完整内容\n                "parent_title": title,                                    # 父章节标题（用于后续合并）\n                "part":
idx,                                              # 子Chunk序号\n                "file_title": section.get("file_title"),                  # 所属文件标题\n            })\n\n
self.logger.debug(f"超长章节切分完成：{title} → 生成{len(sub_sections)}个子Chunk")\n        return sub_sections\n\n```',
        'parent_title': '###### 切分超长章节',
        'part': 2,
        'file_title': 'test'
    },
    {
        'parent_title': '##### 步骤 4: 精细化',
        'title': '###### **关键语法补充说明**',
        'content': '###### **关键语法补充说明**\n\n1、RecursiveCharacterTextSplitter\n\n这是 LangChain 库提供的一个递归字符文本分割器，它会按照指定的分隔符优先级列表，递归地将文本切分成合适大小的片段。\n\n先用
separators 中的第一个分隔符进行切分，切分后如果某个 Chunk 还是超过 chunk_size，则继续用下一个优先级的分隔符切分。\n\n如果所有分隔符都使用了，还是有某个 Chunk 超过 chunk_size （比如一个超长单词），则会在
chunk_size 位置强制切断\n\n2、enumerate\n\n```python\nenumerate(可迭代对象, start=起始值)\n```\n\nenumerate() 用于同时获取索引和对应的元素值，它会返回一个枚举对象，每次迭代产生一个 (索引，元素)
的元组。\n\n```python\n# 不使用 enumerate\nchunks = splitter.split_text(body)\nfor i in range(len(chunks)):\n idx = i + 1  # 手动计算序号\n chunk = chunks[i]\n # 处理逻辑...\n\n# 使用 enumerate\nfor idx, chunk
in enumerate(splitter.split_text(body), start=1):\n # 直接使用 idx 和 chunk\n # 处理逻辑...\n```\n',
        'file_title': 'test'
    },
    {
        'title': '###### 合并过短章节-1',
        'content': '###### 合并过短章节\n\n```python\n    def _merge_short_sections(self, sections: List[Dict[str, str]]) -> List[Dict[str, str]]:\n        """\n
【辅助函数】过短章节合并（减少碎片化，提升检索效果）\n        核心规则：仅合并「同父标题」且「当前块长度不足阈值」的相邻Chunk，避免跨章节合并\n        :param sections:
待合并的Chunk列表（通常是_split_long_section切分后的结果）\n        :return: 合并后的Chunk列表，长度适中，保留元信息\n        """\n        # 边界处理：空列表直接返回，避免后续索引报错\n        if not
sections:\n            self.logger.debug("待合并Chunk列表为空，直接返回")\n            return []\n\n        merged_sections = []  # 最终合并结果\n        current_chunk = None  #
迭代累加器：保存当前待合并的Chunk\n\n        for sec in sections:\n            # 初始化：第一个Chunk直接作为当前待合并块\n            if current_chunk is None:\n                current_chunk = sec\n
continue\n\n            # 合并条件：1.当前块长度不足阈值 2.与下一块同父标题（同属一个原章节）\n            is_current_short = len(current_chunk["content"]) < self.config.min_content_length\n
is_same_parent = current_chunk.get("parent_title") == sec.get("parent_title")\n\n            if is_current_short and is_same_parent:\n                # 合并前清理：去掉下一块开头重复的父标题，避免内容冗余\n
parent_title = sec.get("parent_title", "")\n                next_content = sec["content"]\n                if parent_title and next_content.startswith(parent_title):\n                    next_content =
next_content[len(parent_title):].lstrip()\n                # 合并内容：空行分隔，保证格式整洁\n                current_chunk["content"] += "\\n\\n" + next_content\n                #
更新子Chunk序号：保留最新序号，便于溯源\n                if "part" in sec:\n                    current_chunk["part"] = sec["part"]\n
self.logger.debug(f"合并短Chunk：{current_chunk.get(\'parent_title\')} → 累计长度{len(current_chunk[\'content\'])}")\n            else:\n                # 不满足合并条件：将当前块加入结果，切换为新的待合并块\n
merged_sections.append(current_chunk)\n                current_chunk = sec\n\n        # 循环结束后，将最后一个待合并块加入结果\n        if current_chunk is not None:\n
merged_sections.append(current_chunk)',
        'parent_title': '###### 合并过短章节',
        'part': 1,
        'file_title': 'test'
    },
    {
        'title': '###### 合并过短章节-2',
        'content': '###### 合并过短章节\n\nself.logger.debug(f"短Chunk合并完成：原{len(sections)}个 → 合并后{len(merged_sections)}个")\n        return merged_sections\n```',
        'parent_title': '###### 合并过短章节',
        'part': 2,
        'file_title': 'test'
    },
    {
        'parent_title': '#### 2.4.2 主流程定义',
        'title': '##### 步骤 5: 打印统计',
        'content': '##### 步骤 5: 打印统计\n\n在控制台输出切分结果的简要统计。\n\n```python\n    def _step_5_print_stats(self, lines_count: int, sections: List[Dict[str, str]]) -> None:\n        """\n
【步骤5】输出文档切分统计信息（日志记录，便于监控/调试）\n        :param lines_count: MD原始文本总行数\n        :param sections: 最终处理后的Chunk列表\n        """\n        chunk_num = len(sections)\n        #
输出核心统计信息：原始行数/最终Chunk数/首个Chunk预览\n        self.logger.info("-" * 50 + " 文档切分统计信息 " + "-" * 50)\n        self.logger.info(f"MD原始文本总行数：{lines_count}")\n
self.logger.info(f"最终生成Chunk数量：{chunk_num}")\n```\n',
        'file_title': 'test'
    },
    {
        'parent_title': '#### 2.4.2 主流程定义',
        'title': '##### 步骤 6: 备份',
        'content': '##### 步骤 6: 备份\n\n将结果备份到本地。\n\n```python\n    def _step_6_backup(self, state: ImportGraphState, sections: List[Dict[str, str]]) -> None:\n        """\n
【步骤6】Chunk结果本地JSON备份（便于调试/问题排查，保留处理结果）\n        :param state: 项目状态字典，需包含md_dir（备份目录）\n        :param sections: 最终处理后的Chunk列表\n        """\n\n        try:\n
# 拼接备份文件路径：固定文件名，便于查找\n            backup_path = "D:/doc" / state.get("file_title") / "chunks.json"\n            # 写入JSON文件：保留中文/格式化缩进，便于人工查看\n            with
open(backup_path, "w", encoding="utf-8") as f:\n                """\n                sections是Python 嵌套数据结构（List[Dict[str, str]]，列表里装字典，字典里可能嵌套字符串 / 数字等），而普通文件写入\n
（如f.write(sections)）仅支持写入字符串，直接写 Python 数据结构会报错。\n                json.dump的核心作用就是：将 Python 原生数据结构（列表、字典、字符串、数字等）直接序列化并写入 JSON
文件，无需手动转换为字符串，\n                同时保证数据格式规范、可跨语言 / 跨场景读取，完美适配「Chunk 列表备份」的需求。\n                """\n                json.dump(\n                    sections,\n
f,\n                    #开启 True："title": "\\u4e00\\u7ea7\\u6807\\u9898"（乱码，无法直接看）；\n                    #开启 False："title": "一级标题"（正常中文，人工可直接阅读）。\n
ensure_ascii=False,  # 保留中文，不转义为\\u编码\n                    indent=2             # 格式化缩进，便于阅读\n                )\n
self.logger.info(f"步骤6：Chunk结果备份成功，备份文件路径：{backup_path}")\n        except Exception as e:\n            # 备份失败仅记录日志，不终止主流程\n
self.logger.error(f"步骤6：Chunk结果备份失败，错误信息：{str(e)}", exc_info=False)\n```',
        'file_title': 'test'
    },
    {'parent_title': '#### 2.4.2 主流程定义', 'title': '##### 步骤 7', 'content': '##### 步骤 7\n内容\n', 'file_title': 'test'},
    {'parent_title': '### 2.4 代码实现', 'title': '#### 四级标题', 'content': '#### 四级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '## 2. 节点业务流程', 'title': '### 三级标题', 'content': '### 三级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '# 掌柜智库 - 【导入】文档切片节点', 'title': '## 二级标题', 'content': '## 二级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '', 'title': '# 一级标题', 'content': '# 一级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '# 一级标题', 'title': '## 二级标题', 'content': '## 二级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '', 'title': '# 一级标题', 'content': '# 一级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '# 一级标题', 'title': '## 二级标题', 'content': '## 二级标题\n内容\n', 'file_title': 'test'},
    {'parent_title': '## 二级标题', 'title': '### 三级标题', 'content': '### 三级标题\n内容\n\n\n### 三级标题\n内容\n\n\n### 三级标题\n内容', 'file_title': 'test'}
]
```