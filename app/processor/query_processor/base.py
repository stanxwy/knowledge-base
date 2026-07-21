import logging
import typing
from abc import abstractmethod, ABC

from app.processor.query_processor.state import QueryGraphState
from app.utils.task_utils import add_running_task, add_done_task


T = typing.TypeVar("T", bound="QueryGraphState")

class NodeBase(ABC):

    name: str = "base_node"  # 节点名称，子类应覆盖

    def __init__(self):
        self.logger = logging.getLogger(f"import.{self.name}")

    def __call__(self, state: T) -> T:
        try:
            task_id = state.get("task_id")
            # 1. 开始准备执行节点
            self.logger.info(f"--- {self.name} 开始啦 ---")

            # 开始：记录节点运行状态
            add_running_task(task_id, self.name)

            # 2. 执行节点
            result = self.process(state)

            # 3. 执行节点成功
            self.logger.info(f"--- {self.name} 完成啦 ---")
            
            # 结束：记录节点完成状态
            add_done_task(task_id, self.name)

            return result

        except Exception as e:
            self.logger.error(f"{self.name} 执行失败: {e}")
            raise

    @abstractmethod
    def process(self, state: T) -> T:
        ...