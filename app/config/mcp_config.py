import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DashScopeMcpConfig:
    mcp_base_url: str
    api_key : str

def load_dashscope_mcp_config() -> DashScopeMcpConfig:
    return DashScopeMcpConfig(
        mcp_base_url=os.getenv("MCP_DASHSCOPE_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY")
    )