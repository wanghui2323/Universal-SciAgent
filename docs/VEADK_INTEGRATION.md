# VeADK 原生集成指南

本文档详细说明 Universal-SciAgent 1.0 如何使用 VeADK 的原生功能。

## VeADK 简介

[VeADK (Volcengine Agent Development Kit)](https://github.com/volcengine/veadk-python) 是火山引擎推出的 Agent 开发框架，提供：

- **Agent**: LLM 智能体核心
- **Runner**: Agent 执行器
- **SequentialAgent**: 顺序多智能体编排
- **ParallelAgent**: 并行多智能体编排
- **LoopAgent**: 循环迭代智能体
- **ShortTermMemory**: 短期记忆（会话上下文）
- **LongTermMemory**: 长期记忆（知识库）
- **FunctionTool**: 工具集成

## 模块导入

### 核心模块

```python
# Agent 和 Runner
from veadk import Agent, Runner

# 多智能体编排
from veadk.agents.sequential_agent import SequentialAgent
from veadk.agents.parallel_agent import ParallelAgent
from veadk.agents.loop_agent import LoopAgent

# 记忆系统
from veadk.memory.short_term_memory import ShortTermMemory
from veadk.memory.long_term_memory import LongTermMemory

# 工具系统 (通过 Google ADK)
from google.adk.tools import FunctionTool
```

## 使用示例

### 1. 创建 Agent

```python
from veadk import Agent
from google.adk.tools import FunctionTool

# 定义工具函数
async def search_papers(query: str) -> list:
    """Search academic papers"""
    # Implementation...
    return papers

# 创建 Agent
agent = Agent(
    name="literature_agent",
    description="Expert in literature search",
    instruction="You are a literature research expert...",
    tools=[FunctionTool(search_papers)]
)

# 运行 Agent
result = await agent.run_async("Search for papers on machine learning")
```

### 2. 多智能体编排

```python
from veadk import Agent
from veadk.agents.sequential_agent import SequentialAgent
from veadk.agents.parallel_agent import ParallelAgent

# 创建专家 Agent
literature_agent = Agent(name="literature", instruction="...")
hypothesis_agent = Agent(name="hypothesis", instruction="...")
experiment_agent = Agent(name="experiment", instruction="...")
writing_agent = Agent(name="writing", instruction="...")

# 顺序执行工作流
research_workflow = SequentialAgent(
    name="research_workflow",
    description="Complete research pipeline",
    sub_agents=[
        literature_agent,
        hypothesis_agent,
        experiment_agent,
        writing_agent
    ]
)

result = await research_workflow.run_async("Research topic...")

# 并行执行
parallel_search = ParallelAgent(
    name="parallel_search",
    description="Search multiple sources",
    sub_agents=[arxiv_agent, semantic_scholar_agent, pubmed_agent]
)

results = await parallel_search.run_async("Search query...")
```

### 3. 记忆系统

```python
from veadk.memory.short_term_memory import ShortTermMemory
from veadk.memory.long_term_memory import LongTermMemory

# 短期记忆（会话）
short_term = ShortTermMemory()
session = await short_term.get_session(session_id)
await short_term.create_session(session_id="new_session")

# 长期记忆（知识库）
long_term = LongTermMemory()
doc_id = await long_term.add(content="...", metadata={...})
results = await long_term.search(query="...", top_k=5)
```

### 4. 工具集成

```python
from google.adk.tools import FunctionTool

# 定义工具函数（使用标准 Python 函数）
async def arxiv_search(query: str, max_results: int = 10) -> list:
    """
    Search papers on arXiv.
    
    Args:
        query: Search query
        max_results: Maximum results
    
    Returns:
        List of papers
    """
    # Implementation...
    return papers

# 创建 FunctionTool
arxiv_tool = FunctionTool(arxiv_search)

# 在 Agent 中使用
agent = Agent(
    name="searcher",
    tools=[arxiv_tool]
)
```

## 项目架构

```
Universal-SciAgent1.0/
├── backend/
│   ├── agents/
│   │   ├── base_agent.py         # VeADK Agent 基类封装
│   │   ├── sci_agent_system.py   # SequentialAgent/ParallelAgent 编排
│   │   └── *_agent.py            # 专家 Agent
│   ├── memory/
│   │   └── veadk_memory.py       # ShortTermMemory + LongTermMemory
│   ├── tools/
│   │   └── veadk_tools.py        # FunctionTool 工具
│   └── workflows/
│       └── research_workflow.py  # 工作流编排
└── config.yaml                    # VeADK 配置
```

## 配置

VeADK 自动读取项目根目录的 `config.yaml`：

```yaml
model:
  agent:
    name: ep-xxx  # 火山引擎 ARK 端点 ID
    api_key: your-api-key
    api_base: https://ark.cn-beijing.volces.com/api/v3/
    provider: openai

memory:
  short_term:
    backend: sqlite  # sqlite, mysql, postgresql
    persist_directory: ./data/sessions
  long_term:
    backend: chromadb  # chromadb, vikingdb
    persist_directory: ./data/chromadb
```

## VeADK 版本要求

本项目使用 VeADK v0.2.28+，确保安装正确版本：

```bash
pip install veadk-python>=0.2.28
```

## 参考资源

- [VeADK GitHub](https://github.com/volcengine/veadk-python)
- [VeADK 文档](https://volcengine.github.io/veadk-python/)
- [火山引擎 ARK](https://www.volcengine.com/product/ark)
