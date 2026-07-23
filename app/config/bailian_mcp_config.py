from dataclasses import dataclass
import os

@dataclass(frozen=True)
class McpConfig:
    mcp_base_url: str
    api_key : str

def get_mcp_config() -> McpConfig:
    return McpConfig(
        mcp_base_url=os.getenv("MCP_DASHSCOPE_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY")
    )