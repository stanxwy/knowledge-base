import json
import re
from typing import Tuple, List, Dict, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.processor.import_processor.base import BaseNode
from app.processor.import_processor.exceptions import StateFieldError
from app.processor.import_processor.state import ImportGraphState

class NodeDocumentSplit(BaseNode):
    """
    节点: 文档切分 (node_document_split)
    将长文档切分成小的 Chunks (切片) 以便检索。
    """

    # 覆盖基类的 name 属性，标识节点名称
    name: str = "node_document_split"

    def _step_1_validate_input_state(self, state: ImportGraphState) -> Tuple[str, str]:
        """
        【步骤1】获取并预处理输入数据
        功能：从状态字典中提取MD内容/文件标题/最大长度，做基础标准化
        :param state: 项目状态字典（ImportGraphState），包含md_content等核心键
        :return: 标准化后的MD内容/文件标题
        """
        # 1、非空校验
        file_title = state.get("file_title")
        if not file_title:
            raise StateFieldError(field_name="file_title", message="文件标题不能为空", expected_type=str)

        md_content = state.get("md_content")
        if not md_content:
            raise StateFieldError(field_name="md_content", message="文件内容不能为空", expected_type=str)

        # 2、基础标准化：统一换行符
        md_content = md_content.replace("\r\n", "\n").replace("\r", "\n")

        return md_content, file_title

    def _step_2_split_by_headings(self, content: str, file_title: str) -> Tuple[List[Dict[str, str]], int, int]:
        """
        【步骤2】按Markdown标题初次切分（核心：按#分级切分，跳过代码块内标题）
        LangChain前置预处理：将整份MD按标题拆分为独立章节，为后续精细化切分做基础
        :param content: 标准化后的MD完整内容（字符串）
        :param file_title: 所属文件标题，用于标记章节归属
        :return: 切分后的章节列表/有效标题数量/原始文本总行数
        """

        # 1、定义标题正则
        # 正则匹配Markdown 1-6级标题（核心规则，适配缩进/标准格式）
        # ^\s*：行首允许0/多个空格/Tab（兼容缩进的标题）
        # #{1,6}：匹配1-6个#（对应MD1-6级标题）
        # \s+：#后必须有至少1个空格（区分#是标题还是普通文本）
        # .+：标题文字至少1个字符（避免空标题）
        title_pattern = r'^\s*#{1,6}\s+.+'

        # 2、初始化需要的数据
        lines = content.split("\n")
        sections = [] #章节列表
        title_count = 0 #标题数量
        current_title = "" #当前章节的标题
        current_lines = [] #当前标题和下一个标题之间的文本内容
        in_code_block = False #代码块标记：False当前没在代码块中，True当前在代码块中

        # 3、定义内部函数组装sections列表
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
                #遇到标题现将上一个片段写入sesions，再初始化新的章节
                _flush_section()
                current_title = stripped_line
                current_lines = [current_title]
                title_count += 1
                self.logger.info(f"识别标题：{current_title}")
            else:
                #普通行
                current_lines.append(line)

        _flush_section()
        self.logger.info(f"文档粗切（按标题切分）完成，共{len(sections)}个章节，标题数量是{title_count}，文本共有{len(lines)}行")
        return sections, title_count, len(lines)

    def _step_3_no_headings_fallback(self, content: str, sections: List[Dict[str, str]], title_count: int, file_title: str) -> List[Dict[str, str]]:
        """
        【步骤3】无标题兜底处理
        功能：若MD中未识别到任何标题，将全文作为一个整体处理，避免后续逻辑异常
        :param content: 标准化后的MD完整内容
        :param sections: 步骤2切分后的章节列表
        :param title_count: 步骤2识别的有效标题数量
        :param file_title: 所属文件标题
        :return: 兜底后的章节列表
        """
        if title_count == 0:
            # 无标题情况：替换为单章节，标题为"无标题"
            self.logger.warning(f"步骤3：未识别到任何MD标题，将全文作为单个章节处理，文件：{file_title}")
            return [{"title": "无标题", "content": content, "file_title": file_title}]
        # 有标题情况：直接返回步骤2的结果
        self.logger.debug(f"步骤3：检测到{title_count}个有效标题，无需兜底处理")
        return sections

    def _step_4_finalize_chunks(self, sections: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        【步骤4】Chunk精细化处理（核心：长切短合，适配大模型/检索）
        执行流程：1.切分超长章节 2.合并过短章节 3.父标题兜底（适配Milvus向量库schema）
        :param sections: 步骤3处理后的章节列表
        :return: 长度适中、低碎片化的最终Chunk列表
        """

        # 阶段1：切分超长章节 → 所有章节长度控制在最大长度内
        refined_split = []
        for sec in sections:
            # 对每个章节执行超长切分，结果平铺加入列表（避免嵌套）
            refined_split.extend(self._split_overlong_chunk(sec))
        # self.logger.debug(json.dumps(refined_split, ensure_ascii=False, indent=2))
        self.logger.info(f"步骤4-1：超长章节切分完成，共生成{len(refined_split)}个初始子Chunk")

        # 阶段2：合并过短章节 → 减少碎片化，提升后续检索/大模型调用效果
        final_sections = self._merge_tiny_chunks(refined_split)
        self.logger.info(f"步骤4-2：过短章节合并完成，最终得到{len(final_sections)}个Chunk")

        # 阶段3：父标题兜底 → 适配Milvus向量库schema（parent_title为必填字段）
        # 兜底规则：无parent_title则用自身title，title也无则填空字符串
        # for sec in final_sections:
        #     if not sec.get("parent_title"):
        #         sec["parent_title"] = sec.get("title") or ""
        # self.logger.debug("步骤4-3：父标题兜底完成，所有Chunk均包含parent_title字段")

        return final_sections

    def _split_overlong_chunk(self, section: Dict[str, str]) -> List[Dict[str, str]]:
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
        if len(content) <= self.config.max_content_length:
            return [section]

        # 提取章节标题，用于组装子Chunk前缀（保留标题上下文）
        title = section.get("title", "")
        # 标题前缀：带空行分隔，与正文区分开
        prefix = f"{title}\n\n" if title else ""
        # 计算正文可用长度：总长度 - 标题前缀长度（避免标题占满Chunk额度）
        available_len = self.config.max_content_length - len(prefix)
        # 极端情况：标题长度超过阈值，无法切分，返回原章节
        if available_len <= 0:
            self.logger.warning(f"章节标题过长，无法切分：{title[:20]}...")
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
        chunks = splitter.split_text(body)
        for idx, chunk in enumerate(chunks, start=1):

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

        self.logger.debug(f"超长章节切分完成：{title} → 生成{len(sub_sections)}个子Chunk")
        return sub_sections

    def _merge_tiny_chunks(self, sections: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        【辅助函数】过短章节合并（减少碎片化，提升检索效果）
        核心规则：仅合并「同父标题」且「当前块长度不足阈值」的相邻Chunk，避免跨章节合并
        :param sections: 待合并的Chunk列表（通常是_split_overlong_chunk切分后的结果）
        :return: 合并后的Chunk列表，长度适中，保留元信息
        """
        # 边界处理：空列表直接返回，避免后续索引报错
        if not sections:
            self.logger.debug("待合并Chunk列表为空，直接返回")
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
            is_current_short = len(current_chunk["content"]) < self.config.min_content_length
            is_same_parent = current_chunk.get("parent_title") == sec.get("parent_title")
            self.logger.debug(f'检查短Chunk合并条件：当前块{current_chunk.get("parent_title")}, {sec.get("parent_title")}, 满足合并条件 = {is_same_parent}')

            if is_current_short and is_same_parent:
                # 合并前清理：去掉下一块开头重复的父标题，避免内容冗余
                parent_title = sec.get("parent_title", "")
                next_content = sec["content"]
                if parent_title and next_content.startswith(parent_title):
                    next_content = next_content[len(parent_title):].lstrip()
                # 合并内容：空行分隔，保证格式整洁
                current_chunk["content"] += "\n\n" + next_content
                merge_count += 1
                # 更新子Chunk序号：保留最新序号，便于溯源
                if "part" in sec:
                    current_chunk["part"] = sec["part"]
                self.logger.debug(f"合并短Chunk：{current_chunk.get('parent_title') or current_chunk.get('title')} → 累计长度{len(current_chunk['content'])}，合并Chunk {merge_count} 个")
            else:
                # 不满足合并条件：将当前块加入结果，切换为新的待合并块
                merged_sections.append(current_chunk)
                current_chunk = sec
                merge_count = 1

        # 循环结束后，将最后一个待合并块加入结果
        if current_chunk is not None:
            merged_sections.append(current_chunk)

        self.logger.debug(f"短Chunk合并完成：原{len(sections)}个 → 合并后{len(merged_sections)}个")
        return merged_sections

    def _step_5_print_stats(self, lines_count: int, sections: List[Dict[str, str]]) -> None:
        """
        【步骤5】输出文档切分统计信息（日志记录，便于监控/调试）
        :param lines_count: MD原始文本总行数
        :param sections: 最终处理后的Chunk列表
        """
        chunk_num = len(sections)
        # 输出核心统计信息：原始行数/最终Chunk数/首个Chunk预览
        self.logger.info("-" * 50 + " 文档切分统计信息 " + "-" * 50)
        self.logger.info(f"MD原始文本总行数：{lines_count}")
        self.logger.info(f"最终生成Chunk数量：{chunk_num}")
    
    def _step_6_backup_chunks_json(self, state: ImportGraphState, sections: List[Dict[str, str]]) -> None:
        """
        【步骤6】Chunk结果本地JSON备份（便于调试/问题排查，保留处理结果）
        :param state: 项目状态字典，需包含md_dir（备份目录）
        :param sections: 最终处理后的Chunk列表

        sections是Python 嵌套数据结构（List[Dict[str, str]]，列表里装字典，字典里可能嵌套字符串 / 数字等），而普通文件写入
        （如f.write(sections)）仅支持写入字符串，直接写 Python 数据结构会报错。
        json.dump的核心作用就是：将 Python 原生数据结构（列表、字典、字符串、数字等）直接序列化并写入 JSON 文件，无需手动转换为字符串，
        同时保证数据格式规范、可跨语言 / 跨场景读取，完美适配「Chunk 列表备份」的需求。
        """
        self.backup_json(state, sections, "chunks.json")

    def process(self, state: ImportGraphState) -> ImportGraphState:
        """
        节点：文档切分（node_document_split）
        整体流程：加载输入→按MD标题初切→长切短合→统计输出→结果备份
        核心目的：将长MD文档切分为长度适中的Chunk，适配大模型上下文窗口和向量检索
        后续扩展点：可在各步骤间新增Chunk元信息补充、自定义切分规则、向量入库前置处理等

        必要参数：md_content、file_title
        更新参数：chunks

        :param state: 工作流状态对象
        :return: 更新后的状态对象
        """

        # 步骤1：加载并标准化输入数据
        content, file_title = self._step_1_validate_input_state(state)

        # 步骤2：按MD标题进行初次切分
        sections, title_count, lines_count = self._step_2_split_by_headings(content, file_title)

        # 步骤3：无标题场景兜底处理
        sections = self._step_3_no_headings_fallback(content, sections, title_count, file_title)

        # 步骤4：Chunk精细化处理（长切短合
        sections = self._step_4_finalize_chunks(sections)

        # 步骤5：输出文档切分统计信息
        self._step_5_print_stats(lines_count, sections)

        # 步骤6：Chunk结果本地JSON备份
        self._step_6_backup_chunks_json(state, sections)

        # 写入状态字典
        return { "chunks": sections }


if __name__ == "__main__":
    from app.utils.logger import setup_logging
    logger = setup_logging()

    md_path = "./test_data/output/B530/B530.md"
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    init_state = {
        "md_path": md_path,
        "md_content": md_content,
        "file_title": "B530",
        "output_file_dir": "./test_data/output"
    }
    node_document_split = NodeDocumentSplit()
    result = node_document_split(init_state)

    logger.info(json.dumps(result["chunks"], ensure_ascii=False, indent=4))

"""
(knowledge-base) PS D:\knowledge-base> python -m app.processor.import_processor.nodes.node_document_split
config loaded True...
ImportConfig instance not found...
creating ImportConfig instance...
2026-07-13 20:54:04 - import.node_document_split - INFO - --- node_document_split 开始 ---
2026-07-13 20:54:04 - import.node_document_split - INFO - 识别标题：## HAK 180 烫金机
2026-07-13 20:54:04 - import.node_document_split - INFO - 识别标题：## 警告
2026-07-13 20:54:04 - import.node_document_split - INFO - 识别标题：## 设备
2026-07-13 20:54:04 - import.node_document_split - INFO - 识别标题：## 电源线
2026-07-13 20:54:04 - import.node_document_split - INFO - 识别标题：## 设备
2026-07-13 20:54:04 - import.node_document_split - INFO - 识别标题：## 电源线
2026-07-13 20:54:04 - import.node_document_split - INFO - 识别标题：## 为设备选择一个安全的位置
2026-07-13 20:54:04 - import.node_document_split - INFO - 识别标题：## 设备
2026-07-13 20:54:04 - import.node_document_split - INFO - 识别标题：## 电源线
2026-07-13 20:54:04 - import.node_document_split - INFO - 识别标题：## 警告标签
2026-07-13 20:54:04 - import.node_document_split - INFO - 识别标题：## 设备保修和责任
2026-07-13 20:54:04 - import.node_document_split - INFO - 识别标题：## 设备和电源线
2026-07-13 20:54:04 - import.node_document_split - INFO - 识别标题：## 产品中有害物质的名称及含量
2026-07-13 20:54:04 - import.node_document_split - INFO - 文档粗切（按标题切分）完成，共14个章节，标题数量是13，文本共有182行
2026-07-13 20:54:04 - import.node_document_split - DEBUG - 步骤3：检测到13个有效标题，无需兜底处理
2026-07-13 20:54:04 - import.node_document_split - INFO - 步骤4-1：超长章节切分完成，共生成14个初始子Chunk
2026-07-13 20:54:04 - import.node_document_split - DEBUG - 合并短Chunk：None → 累计长度661
2026-07-13 20:54:04 - import.node_document_split - DEBUG - 合并短Chunk：None → 累计长度1487
2026-07-13 20:54:04 - import.node_document_split - DEBUG - 合并短Chunk：None → 累计长度394
2026-07-13 20:54:04 - import.node_document_split - DEBUG - 合并短Chunk：None → 累计长度799
2026-07-13 20:54:04 - import.node_document_split - DEBUG - 合并短Chunk：None → 累计长度294
2026-07-13 20:54:04 - import.node_document_split - DEBUG - 合并短Chunk：None → 累计长度335
2026-07-13 20:54:04 - import.node_document_split - DEBUG - 合并短Chunk：None → 累计长度414
2026-07-13 20:54:04 - import.node_document_split - DEBUG - 合并短Chunk：None → 累计长度522
2026-07-13 20:54:04 - import.node_document_split - DEBUG - 短Chunk合并完成：原14个 → 合并后6个
2026-07-13 20:54:04 - import.node_document_split - INFO - 步骤4-2：过短章节合并完成，最终得到6个Chunk
2026-07-13 20:54:04 - import.node_document_split - DEBUG - 步骤4-3：父标题兜底完成，所有Chunk均包含parent_title字段
2026-07-13 20:54:04 - import.node_document_split - INFO - -------------------------------------------------- 文档切分统计信息 --------------------------------------------------
2026-07-13 20:54:04 - import.node_document_split - INFO - MD原始文本总行数：182
2026-07-13 20:54:04 - import.node_document_split - INFO - 最终生成Chunk数量：6
2026-07-13 20:54:04 - import.node_document_split - INFO - 步骤6：Chunk结果备份成功，备份文件路径：test_data\output\hak180\chunks.json
2026-07-13 20:54:04 - import.node_document_split - INFO - --- node_document_split 完成 ---
2026-07-13 20:54:04 - root - INFO - [
    {
        "title": "",
        "content": "![](images/677a08ee041965bbbdb6b483d6c17d5aaa36a26b6dc96870a2019f0307b8616f.jpg)  \nD01WD7001-00\n\nSCHN\n\n\n## HAK 180 烫金机\n\n产品安全手册（简体中文）\n\n感谢您购买 HAK 180 烫金机。\n\n在使用本设备之前，请先阅读本手册，包括所有预防措施。阅读本手册后，请妥善保管。\n\n有关使用本设备的更多信息，请参阅使用说明书，其可在兄弟 (中国)商业有限公司技术服务支持网站 http://www.95105369.com/Web/Manuals.aspx 上找到。建议您先通读使用说明书，再使用本设备。\n\n如需获得常见问题解答、故障排除和说明书，请访问\n\nhttp://www.95105369.com。\n\n对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。\n\n•\t对于保养、调整或维修事宜，请联系 Brother 呼叫中心或您当地的Brother 经销商。\n\n•\t如果本设备工作不正常或发生任何错误，请关闭本设备，拔下所有电缆，然后联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t本文档中提供的信息可能会随时更改，恕不另行通知。\n\n•\t严禁未经授权擅自复制或重制本文档的任何部分或全部内容。\n\n•\t请注意，对于使用通过本设备制作的产品造成的任何损坏或利润损失，或者故障、维修导致的数据消失或更改，或者第三方提出的任何索赔，我们不承担任何责任。\n",
        "file_title": "hak180",
        "parent_title": ""
    },
    {
        "title": "## 警告",
        "content": "## 警告\n\n不遵守说明和警告可能导致人员死亡或严重受伤。遵守这些指引以避免冒烟、发热、爆炸、火灾或人员受伤的风险。\n\n\n## 设备\n\n•\t请先阅读这本手册，再尝试操作本设备或尝试进行任何维护。不按照这些说明操作可能会提高发生人员受伤或财产损坏（包括火灾、触电、烧伤或窒息所致）的风险。对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。\n\n•\t请勿在未去除所有包装材料的情况下使用本设备，包括本设备内部的任何附加的包装材料。否则可能会产生火灾的风险。\n\n•\t请勿拆解本设备。拆解本设备可能会导致火灾或触电。\n\n•\t请勿尝试自行维修本设备。打开或拆下盖子可能使您接触到危险电压点以及带来其他风险，并且可能使您的保修失效。对于所有维修事宜，请联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t请在以下环境使用本设备：温度保持在 10 °C 和 32 °C 之间，湿度保持在 20% 和 80% 之间，无冷凝。\n\n•\t请勿使本设备受到阳光直射、过热、接触明火、腐蚀性气体、湿气或灰尘。否则可能产生触电、短路或火灾的风险，从而导致损坏设备和/或导致设备无法运行。\n\n•\t请勿将设备放在加热器、空调、电风扇或水附近。\n\n否则当水（包括加热 空调 通风设备所产生的冷凝水）接触本设备时可能产生短路或火灾的风险。\n\n•\t如果设备变得异常高温、冒烟、产生任何强烈味道，或者如果您意外在设备上倒入任何液体，请立即从电源插座拔掉设备的插头。请联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n如果设备跌落或者已损坏，则有触电的可能性。请从电源插座中拔掉设备的插头，然后联系 呼叫中心或您当地的 经销商。\n\n•\t如果水、其他液体或金属物体进入设备内部，请立即从电源插座中拔掉设备的插头，然后联系 Brother 呼叫中心或您当地的 Brother经销商。\n\n•\t请勿在卡纸或有纸张散落在设备内部的情况下尝试使用本设备。纸张与定影单元长时间接触可能导致火灾。\n\n请勿使用任何易燃物品、任何类型的喷雾剂包含酒精或氨水的有机溶剂/液体来清洁本设备的内部或外部。否则可能导致火灾。请改用无绒干抹布。有关如何清洁本设备的说明，请参阅 。\n\n•\t请勿将本设备放在化学品附近，或者将本设备放置在可能会泼溅到化学品的位置。万一化学品接触本设备，则存在火灾或触电的风险。特别是有机溶剂或液体（如苯、油漆稀释剂、抛光剂或除臭剂）可能导致塑料盖和/或电缆溶解或分解，从而产生火灾或触电的风险。这些化学品或其他化学品可能导致本设备故障或褪色。\n\n•\t本设备的包装中使用了塑料袋。塑料袋并不是玩具。为避免窒息的危险，请将这些塑料袋远离婴儿和儿童，并正确弃置这些塑料袋。\n\n•\t对于使用起搏器的用户：\n\n本设备可能会产生弱磁场。如果您在本设备附近感觉到起搏器工作不正常，请远离本设备，并立即咨询医生。\n\n•\t使用本设备之后短时间内，本设备的一些内部零件仍然处于极热状态。打开前盖时，请勿触摸以灰色标记的区域。存在烧伤的风险。先等待设备冷却下来，再触摸设备的内部零件。\n\n![](images/f3349cded08d6686a93d0a81b9a64ec1e50d9a82cbb88541b37027f085813a15.jpg)  \n儎⑟ഴḽ䆜઀ᛞ࠽व䀜᪮儎⑟Ⲻ䇴༽䜞ԬȾ\n\n![](images/501bb8d2d681e4502d87badb15a68939eadfa086d309c3599f1c36b0bc559177.jpg)\n",
        "file_title": "hak180",
        "parent_title": "## 警告"
    },
    {
        "title": "## 电源线",
        "content": "## 电源线\n\n•\t本设备通过 AC 220 V-240 V 50/60 Hz 电源供电。\n\n请勿将本设备连接到直流电源或逆变器（直流交流变换器）。存在火灾或触电的风险。\n\n•\t请勿用湿手触摸插头。这样可能导致触电。如果不确定您拥有哪种类型的电源，请联系合格的电工。\n\n•\t始终确保插头已完全插入。如果电源线磨损或损坏，请勿使用设备或用手触摸电源线。\n\n•\t设备内部有高压电极。\n\n先拔掉电源线，再清洁设备内部。拔出电源线时，不要拉电线，而是捏住插头往外拔。存在发生火灾、触电或设备故障的风险。\n\n•\t请勿将任何物体压在电源线上。\n\n•\t请勿将本设备放在人们可能踏过电源线的位置。\n\n•\t请勿将本设备放置在会使得拉伸或拉紧电源线的位置，否则电源线可能会磨损或损坏。\n\n•\t始终确保插头已完全插入。如果电源线磨损或损坏，请勿使用设备或用手触摸电源线。如果拔出设备的电源插头，请勿触摸损坏 磨损的部分。\n\n•\t请勿让设备压在电源线上。\n\n•\t请勿在雷暴天气期间使用本设备。存在闪电导致触电的潜在风险。\n\n•\t请勿使用任何非指定的电缆。否则可能导致火灾或人员受伤。必须按照 正确安装。\n\n•\t请勿让任何金属硬件或任何类型的液体落在设备的电源插头上。否则可能导致触电或火灾。\n\n•\tBrother 强烈建议您不要使用任何类型的延长线。\n\n•\t定期拔出电源插头进行清洁。使用干布清洁插头插脚根部以及插脚之间的位置。如果电源插头长时间插入在电源插座中，灰尘会堆积在插头插脚周围，这可能会导致短路，从而引起火灾。\n\n•\t本设备装有接地的插头。此插头只能插入接地的电源插座中。这是一项安全功能。如果您无法将插头插入到插座中，请让电工更换过时的插座。请勿试图破坏接地插头的作用。\n\n不遵守说明和警告可能导致人员中度或严重受伤。遵守这些指引以避免人员受伤。\n",
        "file_title": "hak180",
        "parent_title": "## 电源线"
    },
    {
        "title": "## 设备",
        "content": "## 设备\n\n•\t将本设备放置在平整、水平且稳定的表面上（如桌面），避免震动和冲击。\n\n•\t将本设备放置在通风良好的环境中。\n\n•\t为了防止人员受伤，请谨慎操作，避免将手指放置在图中所示的区域中。\n\n![](images/c61a7f4e923881679f747508ae309c39dc221685344b068009256b1b3a40cc00.jpg)\n\n![](images/5067b2891ca4f761e2874921e0eb433aa742afbf38ca8dc509afecbf0aa6a6b5.jpg)\n\n\n## 电源线\n\n•\t如果您长时间不会使用本设备，请从电源插座中拔掉电源线以确保安全。\n\n•\t本设备必须安装在可轻松使用电源插座的位置附近。如果发生意外情况，必须从电源插座中拔掉电源线以完全关闭电源。\n\n•\t请勿将手放在纸张边缘。纸张锋利的边缘可能导致受伤。\n\n\n## 为设备选择一个安全的位置\n\n•\t提起本设备时，请使用双手抓稳本设备的两侧。如果抓住的是进纸托板和出纸盒，它们可能会掉下来。必须通过将双手放在本设备下面来搬运本设备。\n\n![](images/cc5ee1ac24ebb2707d40dc7a234a8b243f55f5bf08fabc683859be6fdf096ffa.jpg)  \n确保本设备的任何部位均未伸出设备所在的桌面或支架。特别是当本设备位于桌面、支架等边缘时，请勿让出纸盒打开。确保本设备位于平整、水平且稳定的表面上，避免震动。不遵守这些预防措施可能导致设备跌落，从而导致用户的人身伤害以及设备严重损坏。\n\n![](images/8e839864036a7326885565163d99117ea943ecd29a656c85e7aa4052a9b9d28d.jpg)\n\n“重要事项”表示可能导致财产损失或本设备功能丧失的潜在危险情况。\n",
        "file_title": "hak180",
        "parent_title": "## 设备"
    },
    {
        "title": "## 设备",
        "content": "## 设备\n\n如果遵守了操作说明进行操作，但是设备不能正确运行，请仅调整操作说明中涵盖的控制。错误调整其他控制可能导致损坏并且通常需要合格技术进行全面工作以将本设备恢复到正常操作。Brother不建议使用 Brother 正品烫金膜盒以外的其他品牌烫金膜盒。如果使用与本设备不兼容的耗材导致损坏本设备的任何零件，由此导致的任何维修可能不在保修范围内。\n\n\n## 电源线\n\n请勿将设备连接到受墙壁开关或自动计时器控制的电源插座，或者与大型设备或需要大量电力的其他设备连接到同一个电路中。否则可能会损坏电源。电源损坏还可能会从本设备的内存中删除信息，并且反复打开/关闭电源可能会损坏本设备。\n\n\n## 警告标签\n\n请勿撕下或损坏设备上的任何注意/ 警告标签以及序列号标签。\n\n\n## 设备保修和责任\n\n本手册中的任何内容都将不会影响现有设备保修，也不应被视为授予任何其他设备保修。不遵循本手册中的安全说明可能导致本设备的保修失效。\n\n\n## 设备和电源线\n\n•\t请仅使用本设备随附的电源线。\n\n•\t不要在本设备周围放置任何物体。在紧急情况下，此类物体会阻碍接近电源插座。必须保证在需要时可以拔出设备的插头。\n\n•\t请遵守所有适用法规来处理本设备。\n",
        "file_title": "hak180",
        "parent_title": "## 设备"
    },
    {
        "title": "## 产品中有害物质的名称及含量",
        "content": "## 产品中有害物质的名称及含量\n\n<table><tr><td>型号</td><td colspan=\"6\">有害物质</td></tr><tr><td>HAK180</td><td>铅</td><td>汞</td><td>镉</td><td>六价铬</td><td>多溴联苯</td><td>多溴二苯醚</td></tr><tr><td>部件名称</td><td>(Pb)</td><td>(Hg)</td><td>(Cd)</td><td>(Cr(VI))</td><td>(PBB)</td><td>(PBDE)</td></tr><tr><td>框架L单元</td><td>×</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td></tr><tr><td>框架R单元</td><td>×</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td></tr><tr><td>中框架单元</td><td>×</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td></tr><tr><td>框架</td><td>×</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td></tr><tr><td>顶盖单元</td><td>×</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td></tr><tr><td>进纸器单元</td><td>×</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td></tr><tr><td>热熔器</td><td>×</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td></tr><tr><td>盖板</td><td>×</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td></tr><tr><td>标签</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td></tr><tr><td>金属薄片保持单元</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td></tr><tr><td>主电路板</td><td>×</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td></tr><tr><td>低压电源电路板</td><td>×</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td></tr><tr><td>选配件</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td></tr><tr><td>包装材料</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td><td>○</td></tr></table>\n\n本表格依据 的规定编制。\n\n○：表示该有害物质在该部件所有均质材料中的含量均在GB/T26572 规定的限量要求以下。\n\n×：表示该有害物质至少在该部件的某一均质材料中的含量超出规定的限量要求。\n\n（由于技术的原因暂时无法实现替代或减量化）",
        "file_title": "hak180",
        "parent_title": "## 产品中有害物质的名称及含量"
    }
]
"""