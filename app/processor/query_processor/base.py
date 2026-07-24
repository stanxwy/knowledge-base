import logging
import typing
from abc import abstractmethod, ABC

from app.processor.query_processor.state import QueryGraphState
from app.utils.task_utils import add_running_task, add_done_task


T = typing.TypeVar("T", bound="QueryGraphState")

class NodeBase(ABC):

    name: str = "base_node"

    def __init__(self):
        self.logger = logging.getLogger(f"import.{self.name}")

    def __call__(self, state: T) -> T:
        try:
            task_id = state.get("session_id")
            self.logger.info(f"--- {self.name} started ---")
            add_running_task(task_id, self.name)

            result = self.process(state)

            self.logger.info(f"--- {self.name} done ---")
            add_done_task(task_id, self.name)
            return result

        except Exception as e:
            self.logger.error(f"Error running node {self.name}: {e}")
            raise

    @abstractmethod
    def process(self, state: T) -> T:
        ...