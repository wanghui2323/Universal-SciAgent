"""
Universal-SciAgent - Chatbot Mode for AgentKit

This module provides a conversational AI agent for scientific research assistance.
Uses AgentkitAgentServerApp for proper chatbot interface in AgentKit console.
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _normalize_env_vars():
    """Map lowercase env vars to uppercase for VeADK compatibility."""
    mappings = [
        ("model_agent_name", "MODEL_AGENT_NAME"),
        ("model_agent_api_key", "MODEL_AGENT_API_KEY"),
        ("model_agent_api_base", "MODEL_AGENT_API_BASE"),
        ("model_agent_provider", "MODEL_AGENT_PROVIDER"),
        ("model_embedding_name", "MODEL_EMBEDDING_NAME"),
        ("model_embedding_api_key", "MODEL_EMBEDDING_API_KEY"),
        ("model_embedding_api_base", "MODEL_EMBEDDING_API_BASE"),
    ]
    for lower_key, upper_key in mappings:
        lower_val = os.getenv(lower_key)
        if lower_val and not os.getenv(upper_key):
            os.environ[upper_key] = lower_val


# Normalize env vars before imports
_normalize_env_vars()

# Import AgentKit and VeADK
from agentkit.apps import AgentkitAgentServerApp
from veadk import Agent
from veadk.memory.short_term_memory import ShortTermMemory
from google.adk.tools import FunctionTool

# Import tools
from backend.tools.veadk_tools import (
    arxiv_search,
    semantic_scholar_search,
    pubmed_search,
    parse_pdf
)


# =============================================================================
# System Prompt for Conversational Scientific Research Assistant
# =============================================================================
INSTRUCTION = """# 角色
你是 Universal-SciAgent，一个专业的科研助手，擅长帮助用户进行学术研究。

# 目标
1. 帮助用户搜索和分析学术论文
2. 基于文献分析，提出创新性研究假设
3. 为研究假设设计验证实验方案
4. 撰写科研报告和文献综述

# 技能
1. 使用 arxiv_search 搜索 arXiv 论文
2. 使用 semantic_scholar_search 搜索 Semantic Scholar 论文（含引用数据）
3. 使用 pubmed_search 搜索生物医学文献
4. 使用 parse_pdf 解析 PDF 文档

# 支持的研究领域
- 计算机科学 (Computer Science)
- 生物医学 (Biomedical)
- 材料科学 (Materials Science)
- 物理学 (Physics)
- 化学 (Chemistry)

# 工作流程
1. 与用户沟通，明确研究需求和兴趣领域
2. 使用工具搜索相关学术论文
3. 分析文献，总结研究现状和趋势
4. 根据用户需求，生成假设、实验方案或报告

# 约束
1. 必须使用工具进行信息收集
2. 每次搜索限制在 5-10 篇论文，避免信息过载
3. 引用论文时必须给出标题和链接
4. 用中文回答用户问题

# 输出格式
以清晰、结构化的文本形式输出，包括：
- 文献综述：按主题分类的论文摘要
- 假设生成：明确的假设陈述和依据
- 实验方案：详细的步骤和方法
- 报告：专业的学术风格

# 示例
输入："帮我搜索关于大语言模型的最新研究"
输出：
我来帮您搜索大语言模型（LLM）的最新研究论文。

[使用 arxiv_search 工具搜索]

根据搜索结果，以下是最新的研究论文：

1. **论文标题1**
   - 作者：xxx
   - 摘要：xxx
   - 链接：https://arxiv.org/abs/xxx

2. **论文标题2**
   - 作者：xxx
   - 摘要：xxx
   - 链接：https://arxiv.org/abs/xxx

您对哪个方向更感兴趣？我可以进一步深入分析。
"""


# =============================================================================
# Define Tools
# =============================================================================
arxiv_tool = FunctionTool(arxiv_search)
semantic_scholar_tool = FunctionTool(semantic_scholar_search)
pubmed_tool = FunctionTool(pubmed_search)
pdf_tool = FunctionTool(parse_pdf)


# =============================================================================
# Create Short Term Memory (for conversation history)
# =============================================================================
short_term_memory = ShortTermMemory(backend="local")


# =============================================================================
# Create the Agent
# =============================================================================
root_agent = Agent(
    name="universal_sciagent",
    description="Universal Scientific Research Agent - 科研助手",
    instruction=INSTRUCTION,
    tools=[
        arxiv_tool,
        semantic_scholar_tool,
        pubmed_tool,
        pdf_tool
    ],
)

logger.info("Universal-SciAgent initialized successfully")
logger.info(f"Agent name: {root_agent.name}")
logger.info(f"Tools: arxiv_search, semantic_scholar_search, pubmed_search, parse_pdf")


# =============================================================================
# Create AgentKit Agent Server App (for Chatbot UI)
# =============================================================================
agent_server_app = AgentkitAgentServerApp(
    agent=root_agent,
    short_term_memory=short_term_memory
)


# =============================================================================
# Entry point for AgentKit
# =============================================================================
if __name__ == "__main__":
    agent_server_app.run(host="0.0.0.0", port=8000)
