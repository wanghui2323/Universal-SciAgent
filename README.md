# Universal-SciAgent 1.0

> 基于火山引擎 VeADK 原生多智能体框架的通用科研智能体平台

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)
[![VeADK](https://img.shields.io/badge/VeADK-0.2.28+-orange.svg)](https://github.com/volcengine/veadk-python)
[![AgentKit](https://img.shields.io/badge/AgentKit-Deployed-red.svg)](https://github.com/volcengine/agentkit-sdk-python)

## 项目状态

✅ **已部署上线** - AgentKit Runtime

## 🎯 项目简介

Universal-SciAgent 是一个**多智能体科研自动化系统**，完全基于火山引擎 VeADK 原生能力构建：

- **VeADK Agent** 作为智能体核心
- **VeADK SequentialAgent/ParallelAgent** 作为多智能体编排
- **VeADK ShortTermMemory/LongTermMemory** 作为记忆系统
- **VeADK FunctionTool** 作为工具集成
- **AgentKit** 作为云端部署平台
- **火山引擎 ARK (豆包)** 作为底层大模型

## ✨ 功能特性

- 🔬 **多领域支持**: 计算机科学、材料科学、生物医学、物理、化学
- 📚 **文献综述**: 自动搜索和分析学术论文 (arXiv, Semantic Scholar, PubMed)
- 💡 **假设生成**: 基于文献生成研究假设
- 🧪 **实验设计**: 设计验证假设的实验方案
- 📝 **报告撰写**: 生成结构化研究报告
- 🔄 **并行搜索**: 多数据源同时检索
- 🔁 **迭代优化**: 质量反馈循环

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Universal-SciAgent 1.0                          │
├─────────────────────────────────────────────────────────────────────┤
│  VeADK Native Multi-Agent System                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  SequentialAgent (Full Research Workflow)                     │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ │   │
│  │  │ Literature │→│ Hypothesis │→│ Experiment │→│  Writing   │ │   │
│  │  │   Agent    │ │   Agent    │ │   Agent    │ │   Agent    │ │   │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘ │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  ParallelAgent (Parallel Search)                              │   │
│  │  ┌──────────┐ ┌──────────────────┐ ┌──────────┐              │   │
│  │  │  arXiv   │ │ Semantic Scholar │ │  PubMed  │              │   │
│  │  │ Searcher │ │    Searcher      │ │ Searcher │              │   │
│  │  └──────────┘ └──────────────────┘ └──────────┘              │   │
│  └──────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│  VeADK Memory Layer                                                  │
│  ┌─────────────────────────┐  ┌─────────────────────────┐           │
│  │    ShortTermMemory      │  │     LongTermMemory      │           │
│  │  (Session/Conversation) │  │   (Vector Knowledge)    │           │
│  └─────────────────────────┘  └─────────────────────────┘           │
├─────────────────────────────────────────────────────────────────────┤
│  VeADK Tool Layer (FunctionTool)                                     │
│  ┌──────────┐ ┌──────────────────┐ ┌──────────┐ ┌──────────┐        │
│  │  arXiv   │ │ Semantic Scholar │ │  PubMed  │ │ PDF Parse│        │
│  │  Search  │ │     Search       │ │  Search  │ │          │        │
│  └──────────┘ └──────────────────┘ └──────────┘ └──────────┘        │
├─────────────────────────────────────────────────────────────────────┤
│                    VeADK Agent + Runner Core                         │
├─────────────────────────────────────────────────────────────────────┤
│                火山引擎 ARK API (豆包大模型)                           │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      AgentKit Runtime                                │
│                     (VeFaaS 云端部署)                                │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔧 VeADK 原生功能使用

### 多智能体编排

```python
from veadk import Agent
from veadk.agents.sequential_agent import SequentialAgent
from veadk.agents.parallel_agent import ParallelAgent
from google.adk.tools import FunctionTool

# 创建专家 Agent
literature_agent = Agent(
    name="literature_agent",
    description="Literature research expert",
    instruction="Search and analyze academic papers...",
    tools=[FunctionTool(arxiv_search), FunctionTool(semantic_scholar_search)]
)

hypothesis_agent = Agent(
    name="hypothesis_agent",
    description="Hypothesis generation expert",
    instruction="Generate research hypotheses..."
)

# 使用 SequentialAgent 编排工作流
research_workflow = SequentialAgent(
    name="research_workflow",
    description="Complete research pipeline",
    sub_agents=[literature_agent, hypothesis_agent, experiment_agent, writing_agent]
)

# 执行工作流
result = await research_workflow.run_async("Research topic...")
```

### 记忆系统

```python
from veadk.memory.short_term_memory import ShortTermMemory
from veadk.memory.long_term_memory import LongTermMemory

# 短期记忆 (会话上下文)
short_term = ShortTermMemory()
session = await short_term.get_session(session_id)

# 长期记忆 (知识库)
long_term = LongTermMemory()
doc_id = await long_term.add(content="...", metadata={...})
results = await long_term.search(query="...", top_k=5)
```

### 工具集成

```python
from google.adk.tools import FunctionTool

async def arxiv_search(query: str, max_results: int = 10) -> List[Dict]:
    """Search papers on arXiv"""
    # Implementation...
    return papers

# 创建 VeADK FunctionTool
arxiv_tool = FunctionTool(arxiv_search)

# 在 Agent 中使用
agent = Agent(
    name="search_agent",
    tools=[arxiv_tool]
)
```

## 🔧 技术栈

| 层级 | 技术 | VeADK 模块 |
|------|------|------------|
| **Agent 核心** | [VeADK](https://github.com/volcengine/veadk-python) | `veadk.Agent`, `veadk.Runner` |
| **多智能体** | VeADK Native | `veadk.agents.SequentialAgent`, `veadk.agents.ParallelAgent`, `veadk.agents.LoopAgent` |
| **记忆系统** | VeADK Native | `veadk.memory.ShortTermMemory`, `veadk.memory.LongTermMemory` |
| **工具系统** | Google ADK (VeADK 底层) | `google.adk.tools.FunctionTool` |
| **云端部署** | [AgentKit](https://github.com/volcengine/agentkit-sdk-python) | 一键部署到 VeFaaS |
| **大模型** | 火山引擎 ARK | doubao-pro-32k / doubao-pro-128k |
| **文献检索** | arXiv, Semantic Scholar, PubMed | 自定义 FunctionTool |

## 🚀 快速开始

### 1. 环境准备

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置

创建 `config.yaml`（参考 `config.yaml.example`）：

```yaml
model:
  agent:
    name: your-endpoint-id
    api_key: your-api-key
    api_base: https://ark.cn-beijing.volces.com/api/v3/
    provider: openai

memory:
  short_term:
    backend: sqlite  # or mysql, postgresql
  long_term:
    backend: chromadb  # or vikingdb
```

### 3. 本地运行

```bash
python agent.py
# 服务启动在 http://localhost:8000
```

### 4. 部署到 AgentKit

```bash
pip install agentkit-sdk-python
agentkit init
agentkit launch
```

## 📁 项目结构

```
Universal-SciAgent1.0/
├── agent.py                    # AgentKit 入口点
├── config.yaml                 # VeADK 配置
├── backend/
│   ├── agents/
│   │   ├── base_agent.py       # VeADK Agent 基类
│   │   ├── sci_agent_system.py # 多智能体系统 (SequentialAgent)
│   │   └── *_agent.py          # 专家 Agent
│   ├── tools/
│   │   └── veadk_tools.py      # FunctionTool 工具
│   ├── memory/
│   │   └── veadk_memory.py     # ShortTermMemory + LongTermMemory
│   ├── workflows/
│   │   └── research_workflow.py # 工作流编排
│   └── core/
│       └── config.py           # 配置管理
├── config/
│   ├── agentkit_deploy.yaml    # AgentKit 部署配置
│   └── domains/                # 领域配置
├── tests/                      # 测试代码
└── docs/                       # 详细文档
```

## 📖 API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/domains` | GET | 获取支持的研究领域 |
| `/invoke` | POST | 通用调用入口 |
| `/literature-review` | POST | 文献综述 |
| `/full-research` | POST | 完整研究流程 |

## 🧪 测试

```bash
pytest tests/ -v
```

## 📚 文档

- [快速开始](docs/QUICKSTART.md)
- [安装指南](docs/INSTALL.md)
- [部署指南](docs/DEPLOYMENT_GUIDE.md)
- [架构说明](docs/ARCHITECTURE.md)
- [VeADK 集成](docs/VEADK_INTEGRATION.md)

## 🔗 相关资源

- [VeADK 官方文档](https://volcengine.github.io/veadk-python/)
- [VeADK GitHub](https://github.com/volcengine/veadk-python)
- [AgentKit SDK](https://github.com/volcengine/agentkit-sdk-python)
- [AgentKit Samples](https://github.com/volcengine/agentkit-samples)

## 📄 License

[Apache 2.0](LICENSE)

---

**Made with ❤️ using VeADK Native Multi-Agent + AgentKit**
