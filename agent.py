"""
Universal-SciAgent - Chatbot Mode for AgentKit

This module provides a conversational AI agent for scientific research assistance.
Supports multi-turn dialogue with memory and streaming responses.
"""
import os
import logging
from typing import List, Dict, Any, Optional

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

# Import VeADK
from veadk import Agent
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
SYSTEM_PROMPT = """你是 Universal-SciAgent，一个专业的科研助手。

## 你的能力
1. **文献检索**: 使用 arxiv_search、semantic_scholar_search、pubmed_search 工具搜索论文
2. **假设生成**: 基于文献分析，提出创新性研究假设
3. **实验设计**: 为研究假设设计验证实验方案
4. **报告撰写**: 撰写科研报告和文献综述

## 支持的研究领域
- 计算机科学 (Computer Science)
- 生物医学 (Biomedical)
- 材料科学 (Materials Science)
- 物理学 (Physics)
- 化学 (Chemistry)

## 对话风格
- 友好专业，用中文回答
- 主动询问用户需求
- 提供结构化的研究建议
- 引用具体论文时给出标题和链接

## 工具使用
当用户询问研究主题时，主动使用搜索工具获取最新文献。
每次搜索限制在 5-10 篇论文，避免信息过载。

开始对话时，先问候用户并询问他们的研究兴趣。
"""


# =============================================================================
# Define Tools as FunctionTools for the Agent
# =============================================================================

# Wrap tools with FunctionTool
arxiv_tool = FunctionTool(arxiv_search)
semantic_scholar_tool = FunctionTool(semantic_scholar_search)
pubmed_tool = FunctionTool(pubmed_search)
pdf_tool = FunctionTool(parse_pdf)


# =============================================================================
# Create the Conversational Agent (Module-level for AgentKit)
# =============================================================================

agent = Agent(
    name="universal_sciagent",
    system_prompt=SYSTEM_PROMPT,
    tools=[
        arxiv_tool,
        semantic_scholar_tool,
        pubmed_tool,
        pdf_tool
    ]
)

logger.info("Universal-SciAgent (Chatbot Mode) initialized successfully")
logger.info(f"Agent name: {agent.name}")
logger.info(f"Tools: arxiv_search, semantic_scholar_search, pubmed_search, parse_pdf")


# =============================================================================
# Optional: Local testing server
# =============================================================================

if __name__ == "__main__":
    import asyncio
    from veadk import Runner
    
    async def chat():
        """Interactive chat for local testing."""
        runner = Runner(agent=agent)
        session_id = "local-test-session"
        
        print("\n" + "="*60)
        print("🔬 Universal-SciAgent 对话模式")
        print("="*60)
        print("输入 'quit' 或 'exit' 退出")
        print("="*60 + "\n")
        
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 再见！祝您研究顺利！")
                    break
                
                if not user_input:
                    continue
                
                print("\n🤖 SciAgent: ", end="", flush=True)
                
                # Run agent with streaming
                response = await runner.run(
                    messages=user_input,
                    user_id="local_user",
                    session_id=session_id
                )
                
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
    
    # Run the chat loop
    asyncio.run(chat())
