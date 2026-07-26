import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.getLogger().info("entering...")

import re
from rich import print as rprint
from typing import List, Dict, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.workflows.ingestion.import_config import get_config

logging.getLogger().info("starting...")
stripped_line = "````123~~~abc```````"
# 方法2: 保持原有的 match 方式，但更清晰
code_block_marker_match = re.match(r'^(`{3,}|~{3,}).*?(`{3,}|~{3,}).*?(`{3,}|~{3,})$', stripped_line)
if code_block_marker_match:
    marker1 = code_block_marker_match.group(1)
    marker2 = code_block_marker_match.group(2)
    marker3 = code_block_marker_match.group(3)
    print(f"标记1: {marker1}")
    print(f"标记2: {marker2}")
    print(f"标记3: {marker3}")

def split_by_titles_v1(content: str, file_title: str):
        title_pattern = r'^\s*#{1,6}\s+.+'

        # 2、初始化需要的数据
        lines = content.split("\n")
        sections = [] #章节列表
        title_count = 0 #标题数量
        current_title = "" #当前章节的标题
        current_lines = [] #当前标题和下一个标题之间的文本内容
        in_code_block = False #代码块标记：False当前没在代码块中，True当前在代码块中

        def _flush_section():
            """内部辅助函数：将当前缓存的章节写入sections，空缓存则跳过"""
            if not current_lines:
                return
            sections.append({
                "title": current_title,
                # 每段使用 \n换行区分
                "content": "\n".join(current_lines),
                "file_title": file_title,
            })

        # 4、逐行遍历，识别标题和普通行以及代码快
        for line in lines:
            stripped_line = line.strip()

            # 4.1 识别代码快边界 ``` 或 ~~~
            if stripped_line.startswith("```") or stripped_line.startswith("~~~"):
                in_code_block = not in_code_block
                current_lines.append(line)
                continue

            # 4.2 识别标题
            is_valid_title = (not in_code_block) and re.match(title_pattern, line)
            if is_valid_title:
                #遇到标题现将上一个片段写入sesions，再初始化新的章节
                _flush_section()
                current_title = stripped_line
                current_lines = [current_title]
                title_count += 1
                print(f"识别标题：{current_title}")
            else:
                #普通行
                current_lines.append(line)

        _flush_section()
        print(f"文档粗切（按标题切分）完成，共{len(sections)}个章节，标题数量是{title_count}，文本共有{len(lines)}行")
        return sections, title_count, len(lines)


def split_by_titles_v2(content: str, file_title: str):
    title_pattern = r'^\s*#{1,6}\s+.+'

    lines = content.split("\n")
    sections = [] #章节列表
    title_count = 0 #标题数量
    current_title = "" #当前章节的标题
    current_lines = [] #当前标题和下一个标题之间的文本内容
    in_code_block = False #代码块标记：False当前没在代码块中，True当前在代码块中

    def _flush_section():
        """内部辅助函数：将当前缓存的章节写入sections，空缓存则跳过"""
        if not current_lines:
            return
        sections.append({
            "parent_title": _find_parent_title(current_title, sections),
            "title": current_title,
            # 每段时间使用 \n换行区分
            "content": "\n".join(current_lines),
            "file_title": file_title,
        })
    
    
    def _find_parent_title(current_title: str, sections: List[Dict[str, str]]) -> str:
        """
        根据当前标题，在已处理的 sections 中查找最近的父标题
        
        :param current_title: 当前标题（如 "### 三级"）
        :param sections: 已切分的章节列表（每个元素包含 title 字段）
        :return: 父标题文本，如果没有找到则返回空字符串
        """
        # 1. 计算当前标题的级别（# 的数量）
        current_level = _get_title_level(current_title)
        if current_level is None or current_level == 1:
            return ""  # 如果不是合法标题，返回空
        
        # 2. 从后往前遍历 sections，找到第一个级别比当前标题更低的标题
        #    比如当前是 ###（3级），找 ##（2级）或 #（1级）
        for section in reversed(sections):
            parent_title = section.get("title", "")
            parent_level = _get_title_level(parent_title)
            
            if parent_level is not None and parent_level < current_level:
                # 找到了更高级别（数字更小）的标题
                return parent_title
        # 3. 如果没有找到父标题（比如当前是 # 一级标题）
        return ""

    def _get_title_level(title: str) -> Optional[int]:
        """
        提取标题级别（# 的数量）
        
        :param title: 标题文本（如 "### 三级"）
        :return: 级别数字（1-6），如果不是合法标题返回 None
        """
        if not title:
            return None
        # 匹配开头的 # 号
        match = re.match(r'^(#{1,6})\s+', title)
        if not match:
            return None
        # 返回 # 的数量（级别）
        return len(match.group(1))


    # 4、逐行遍历，识别标题和普通行以及代码快
    for line in lines:
        stripped_line = line.strip()
        # 4.1 识别代码块边界 ```、~~~、````、~~~~ 等（至少 3 个连续字符）
        # 使用正则匹配：行首到行尾只有 ` 或 ~ 字符，且数量>=3
        code_block_marker_match = re.match(r'^(`{3,}|~{3,})', stripped_line)
        if code_block_marker_match:
            marker = code_block_marker_match.group(1)

            if not in_code_block:
                # 进入代码块，记录开始的标记特征
                in_code_block = True
                code_block_start_marker = marker
            elif in_code_block and stripped_line == code_block_start_marker:
                # 遇到匹配的结束标记（相同字符且相同长度）
                in_code_block = False
                code_block_start_marker = None

            current_lines.append(line)
            continue

        # 4.2 识别标题
        is_valid_title = (not in_code_block) and re.match(title_pattern, line)
        if is_valid_title:
            #遇到标题现将上一个片段写入sections，再初始化新的章节
            _flush_section()
            current_title = stripped_line
            current_lines = [current_title]
            title_count += 1
            print(f"识别标题：{current_title}")
        else:
            #普通行
            current_lines.append(line)

    _flush_section()
    print(f"文档粗切（按标题切分）完成，共{len(sections)}个章节，标题数量是{title_count}，文本共有{len(lines)}行")
    return sections, title_count, len(lines)


def split_long_section(section: Dict[str, str]) -> List[Dict[str, str]]:
        """
        【辅助函数】超长章节二次切分（核心适配LangChain分割器）
        功能：单个章节内容超限时，按「段落→句子→空格」从粗到细切分，保留语义
        切分规则：1.先按空行(段落) 2.再按换行 3.最后按中英文标点/空格
        :param section: 原始章节字典，必须包含content键，可选title/file_title等
        :return: 切分后的子章节列表，每个子章节带父标题/序号等元信息
        """
        # 内容空值兜底：无内容直接返回原章节
        content = section.get("content", "")
        # 长度未超限，无需切分，直接返回原章节（列表格式保持统一）
        if len(content) <= get_config().max_content_length:
            return [section]

        # 提取章节标题，用于组装子Chunk前缀（保留标题上下文）
        title = section.get("title", "")
        # 标题前缀：带空行分隔，与正文区分开
        prefix = f"{title}\n\n" if title else ""
        # 计算正文可用长度：总长度 - 标题前缀长度（避免标题占满Chunk额度）
        available_len = get_config().max_content_length - len(prefix)
        # 极端情况：标题长度超过阈值，无法切分，返回原章节
        if available_len <= 0:
            print(f"章节标题过长，无法切分：{title[:20]}...")
            return [section]

        # 清理正文重复标题：避免原章节中正文开头重复标题，导致子Chunk内容冗余
        body = content
        if title and body.lstrip().startswith(title):
            body = body[body.find(title) + len(title):].lstrip()

        # 初始化LangChain递归分割器（核心工具：按优先级分隔符切分，保留语义）
        # separators：分割符优先级（从粗到细），优先按大语义单元切分，最后才硬拆
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=available_len,  # 正文部分最大长度（已扣除标题）
            chunk_overlap=0,           # 无重叠：按标题切分后语义完整，无需重叠
            # 分割符优先级：空行(段落)→换行→中文标点→英文标点→空格，最后硬拆（在 chunk_size 位置强制切断）
            # 先用第一个分隔符进行切分，切分后如果某个 Chunk 还是超过 chunk_size，则继续用下一个优先级的分隔符切分
            separators=["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?", ";", " "],
        )

        # 切分正文并组装子章节（带完整元信息，便于溯源）
        sub_sections = []

        # 遍历切分后的每个文本块，idx 从 1 开始计数
        for idx, chunk in enumerate(splitter.split_text(body), start=1):

            # 清理空内容：跳过切分后的空字符串
            text = chunk.strip()
            if not text:
                continue

            # 组装子Chunk完整内容 = 标题前缀 + 切分后的正文
            full_text = (prefix + text).strip()

            # 子章节元信息：保留父级关联，添加序号，便于后续检索/溯源
            sub_sections.append({
                "title": f"{title}-{idx}" if title else f"chunk-{idx}",   # 子Chunk标题（带序号）
                "content": full_text,                                     # 切分后的完整内容
                "parent_title": title,                                    # 父章节标题（用于后续合并）
                "part": idx,                                              # 子Chunk序号
                "file_title": section.get("file_title"),                  # 所属文件标题
            })

        print(f"超长章节切分完成：{title} → 生成{len(sub_sections)}个子Chunk")
        return sub_sections

def merge_short_sections(sections: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    【辅助函数】过短章节合并（减少碎片化，提升检索效果）
    核心规则：仅合并「同父标题」且「当前块长度不足阈值」的相邻Chunk，避免跨章节合并
    :param sections: 待合并的Chunk列表（通常是_split_long_section切分后的结果）
    :return: 合并后的Chunk列表，长度适中，保留元信息
    """
    # 边界处理：空列表直接返回，避免后续索引报错
    if not sections:
        print("待合并Chunk列表为空，直接返回")
        return []

    merged_sections = []  # 最终合并结果
    current_chunk = None  # 迭代累加器：保存当前待合并的Chunk
    merge_count = 1

    for sec in sections:
        # 初始化：第一个Chunk直接作为当前待合并块
        if current_chunk is None:
            current_chunk = sec
            continue

        # 合并条件：1.当前块长度不足阈值 2.与下一块同父标题（同属一个原章节）
        is_current_short = len(current_chunk["content"]) < get_config().min_content_length
        is_same_parent = current_chunk.get("parent_title") == sec.get("parent_title")
        print(current_chunk.get("parent_title"), sec.get("parent_title"), "满足合并条件 =", is_same_parent)

        if is_current_short and is_same_parent:
            # 合并前清理：去掉下一块开头重复的父标题，避免内容冗余
            parent_title = sec.get("parent_title", "")
            next_content = sec["content"]
            if parent_title and next_content.startswith(parent_title):
                next_content = next_content[len(parent_title):].lstrip()
            # 合并内容：空行分隔，保证格式整洁
            current_chunk["content"] += "\n\n" + next_content
            # 更新子Chunk序号：保留最新序号，便于溯源
            if "part" in sec:
                current_chunk["part"] = sec["part"]
            merge_count += 1
            print(f"合并短Chunk：{current_chunk.get('parent_title') or current_chunk.get('title')} → 累计长度{len(current_chunk['content'])}，合并Chunk {merge_count} 个")
        else:
            # 不满足合并条件：将当前块加入结果，切换为新的待合并块
            merged_sections.append(current_chunk)
            current_chunk = sec
            merge_count = 1

    # 循环结束后，将最后一个待合并块加入结果
    if current_chunk is not None:
        merged_sections.append(current_chunk)

    print(f"短Chunk合并完成：原{len(sections)}个 → 合并后{len(merged_sections)}个")
    return merged_sections


with open("./test_data/kb/07【掌柜智库】【导入】文档切片.md", "r", encoding="utf-8") as f:
    content = f.read()
sections, _, _ = split_by_titles_v2(content, "test")
rprint(sections)

refined = []
for sec in sections:
    refined.extend(split_long_section(sec))
rprint("refined", refined)

final = merge_short_sections(refined)
rprint("final", final)